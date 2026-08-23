from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Mapping
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.export_publication import (
    CHECKSUMS_FILE,
    GENERATED_MANIFEST,
    MANIFEST_PATH,
    PublicationExportError,
    SnapshotFile,
    export_snapshot,
    generated_metadata,
    normalize_public_path,
    parse_manifest,
    resolved_local_target,
    validate_snapshot,
    verify_snapshot,
)
from scripts import export_publication


class TemporaryGitRepository:
    def __init__(self, root: Path):
        self.root = root

    def run(self, *args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
        )

    def write(self, path: str, data: str | bytes) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            target.write_text(data, encoding="utf-8")
        else:
            target.write_bytes(data)

    def commit(self) -> None:
        self.run("add", ".")
        self.run("commit", "-m", "Test publication snapshot")


def create_repository(root: Path) -> TemporaryGitRepository:
    root.mkdir(parents=True)
    repo = TemporaryGitRepository(root)
    repo.run("init", "-b", "main")
    repo.run("config", "user.name", "Canary " + "Personal Name")
    repo.run("config", "user.email", "canary" + "@" + "example.invalid")
    return repo


def valid_files() -> dict[str, str]:
    return {
        "README.md": "# Home | 首页\n\n[Guide | 指南](docs/guide.md)\n",
        "docs/guide.md": "# Guide | 指南\n\n[Home | 首页](../README.md)\n",
        MANIFEST_PATH: ("README.md\n" "docs/guide.md\n" f"{MANIFEST_PATH}\n"),
    }


def manifest_text(*paths: str) -> str:
    return "".join(f"{path}\n" for path in sorted(paths))


def write_export_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    os.utime(
        path,
        (export_publication.SOURCE_DATE_EPOCH, export_publication.SOURCE_DATE_EPOCH),
    )


class ManifestValidationTests(unittest.TestCase):
    def test_rejects_cross_platform_and_private_paths(self) -> None:
        invalid = (
            "../private.md",
            "/absolute.md",
            "C:" + "\\Users\\" + "person\\note.md",
            "docs\\guide.md",
            ".Git/config.md",
            "docs/.env.md",
            "docs/private/note.md",
            "./guide.md",
            "docs/hidden\u202e.md",
            "docs/CON.md",
            "docs/file.md:stream.md",
            "docs/trailing./note.md",
            ".GitHub/note.md",
            "Scripts/note.md",
            "Teaching_memo/note.md",
        )
        for path in invalid:
            with self.subTest(path=path), self.assertRaises(PublicationExportError):
                normalize_public_path(path)

    def test_rejects_casefold_collision_and_unsorted_manifest(self) -> None:
        collision = ("A.md\n" "a.md\n" f"{MANIFEST_PATH}\n").encode()
        with self.assertRaises(PublicationExportError) as context:
            parse_manifest(collision)
        self.assertEqual("MANIFEST_DUPLICATE_OR_CASE_COLLISION", context.exception.code)

        unsorted = ("z.md\n" "a.md\n" f"{MANIFEST_PATH}\n").encode()
        with self.assertRaises(PublicationExportError) as context:
            parse_manifest(unsorted)
        self.assertEqual("MANIFEST_NOT_SORTED", context.exception.code)

    def test_rejects_encoded_escape_unsafe_scheme_and_git_host(self) -> None:
        for target, expected_code in (
            ("../../private.md", "SNAPSHOT_LINK_ESCAPES_ROOT"),
            ("%2e%2e/%2e%2e/private.md", "SNAPSHOT_LINK_ESCAPES_ROOT"),
            ("file:///etc/passwd", "SNAPSHOT_LINK_SCHEME_FORBIDDEN"),
            ("javascript:alert(1)", "SNAPSHOT_LINK_SCHEME_FORBIDDEN"),
            ("//example.org/file.md", "SNAPSHOT_PROTOCOL_RELATIVE_LINK_FORBIDDEN"),
            ("https://github.com/example/project", "SNAPSHOT_GIT_HOST_LINK_FORBIDDEN"),
            (
                "https://%67ithub.com/example/project",
                "SNAPSHOT_GIT_HOST_LINK_FORBIDDEN",
            ),
            (
                "https://github&#46;com/example/project",
                "SNAPSHOT_GIT_HOST_LINK_FORBIDDEN",
            ),
            (
                "https\\://github.com/example/project",
                "SNAPSHOT_GIT_HOST_LINK_FORBIDDEN",
            ),
            (
                "javascript&colon;alert(1)",
                "SNAPSHOT_LINK_SCHEME_FORBIDDEN",
            ),
            (
                "&sol;&sol;example.org/file.md",
                "SNAPSHOT_PROTOCOL_RELATIVE_LINK_FORBIDDEN",
            ),
            ("https:////github.com/example/project", "SNAPSHOT_LINK_URL_INVALID"),
            ("https:private.md", "SNAPSHOT_LINK_URL_INVALID"),
            ("https://[bad", "SNAPSHOT_LINK_URL_INVALID"),
        ):
            with self.subTest(target=target):
                with self.assertRaises(PublicationExportError) as context:
                    resolved_local_target("README.md", target)
                self.assertEqual(expected_code, context.exception.code)
        self.assertIsNone(
            resolved_local_target("README.md", "https://example.org/source")
        )

    def test_entity_decoded_traversal_cannot_bypass_allowlist(self) -> None:
        data = b"[Private](decoy.md&sol;..&sol;private.md)\n"
        file = SnapshotFile("README.md", data, "0" * 64)

        with self.assertRaises(PublicationExportError) as context:
            validate_snapshot([file])

        self.assertEqual("SNAPSHOT_LINK_OUTSIDE_ALLOWLIST", context.exception.code)

    def test_rejects_remote_markdown_image(self) -> None:
        data = b"![remote](https://example.org/tracker.png)\n"
        file = SnapshotFile("README.md", data, "0" * 64)
        with self.assertRaises(PublicationExportError) as context:
            validate_snapshot([file])
        self.assertEqual("SNAPSHOT_MARKDOWN_IMAGE_FORBIDDEN", context.exception.code)

    def test_rejects_nested_and_reference_style_links(self) -> None:
        cases = (
            "[See [private]](../private.md)\n",
            "![alt [nested]](https://example.org/tracker.png)\n",
            "[![nested image](https://example.org/tracker.png)](README.md)\n",
            "![alt][pic]\n[pic]: https://example.org/tracker.png\n",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(PublicationExportError):
                data = text.encode("utf-8")
                validate_snapshot([SnapshotFile("README.md", data, "0" * 64)])

        escaped = b"\\![literal image syntax]\n"
        validate_snapshot([SnapshotFile("README.md", escaped, "0" * 64)])

    def test_rejects_visible_git_host_even_outside_markdown_links(self) -> None:
        cases = (
            "http://github.com/example/project\n",
            "`https://github.com/example/project`\n",
            "https://%67ithub.com/example/project\n",
            "github.com/example/project\n",
        )
        for text in cases:
            with self.subTest(text=text):
                with self.assertRaises(PublicationExportError) as context:
                    validate_snapshot(
                        [SnapshotFile("README.md", text.encode("utf-8"), "0" * 64)]
                    )
                self.assertEqual(
                    "SNAPSHOT_GIT_HOST_LINK_FORBIDDEN", context.exception.code
                )

    def test_rejects_privacy_data_split_by_commonmark_rendering(self) -> None:
        cases = (
            "private&#64;example&#46;com\n",
            "312&#45;555&#45;1234\n",
            "private\\@example\\.com\n",
            "312\\-555\\-1234\n",
            "private@example.**com**\n",
            "312-555-**1234**\n",
            "git**hub**.com/owner\n",
            "private@example.$com$\n",
            "312-$555$-1234\n",
            "git$hub$.com/owner\n",
            "[private](README.md)@example.com\n",
            "private@example.[com](README.md)\n",
            "312-[555](README.md)-1234\n",
            "git[hub](README.md).com/owner\n",
            "[pri[vat](README.md)e](README.md)@example.com\n",
            "private@example.\u200bcom\n",
            "git\u200bhub.com/owner\n",
            'private@example.<a id="x"></a>com\n',
            "private@example.<br>com\n",
            "git<br>hub.com/owner\n",
            "[contact](https://example.org/?e=private%40example.com)\n",
            "[call](https://example.org/?phone=312%2D555%2D1234)\n",
            "[contact](https://example.org/?e=private&#37;40example&#46;com)\n",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(PublicationExportError):
                validate_snapshot(
                    [SnapshotFile("README.md", text.encode("utf-8"), "0" * 64)]
                )

    def test_rejects_bidi_format_controls_that_reorder_private_data(self) -> None:
        cases = (
            "\u202emoc.elpmaxe@etavirp\u202c\n",
            "\u202e4321-555-213\u202c\n",
            "\u202erenwo/moc.buhtig\u202c\n",
        )
        for text in cases:
            with self.subTest(text=text):
                with self.assertRaises(PublicationExportError) as context:
                    validate_snapshot(
                        [SnapshotFile("README.md", text.encode("utf-8"), "0" * 64)]
                    )
                self.assertEqual(
                    "SNAPSHOT_UNICODE_FORMAT_CHARACTER_FORBIDDEN",
                    context.exception.code,
                )

    def test_rejects_inline_math_that_reconstructs_private_data(self) -> None:
        cases = (
            r"$\text{private@example.}\text{com}$" + "\n",
            r"$312-\text{555}-1234$" + "\n",
            r"$\text{git}\text{hub.com/owner}$" + "\n",
        )
        for text in cases:
            with self.subTest(text=text):
                with self.assertRaises(PublicationExportError) as context:
                    validate_snapshot(
                        [SnapshotFile("README.md", text.encode("utf-8"), "0" * 64)]
                    )
                self.assertEqual(
                    "SNAPSHOT_UNESCAPED_DOLLAR_FORBIDDEN", context.exception.code
                )

    def test_unescaped_dollar_detection_obeys_backslash_parity(self) -> None:
        for text in (r"Price: \$5." + "\n", r"Price: \\\$5." + "\n"):
            validate_snapshot(
                [SnapshotFile("README.md", text.encode("utf-8"), "0" * 64)]
            )

        with self.assertRaises(PublicationExportError) as context:
            validate_snapshot(
                [
                    SnapshotFile(
                        "README.md", (r"Price: \\$5." + "\n").encode("utf-8"), "0" * 64
                    )
                ]
            )
        self.assertEqual("SNAPSHOT_UNESCAPED_DOLLAR_FORBIDDEN", context.exception.code)

    def test_rejects_math_fences_that_reconstruct_private_data(self) -> None:
        cases = (
            "```math\n" + r"\text{private@example.}\text{com}" + "\n```\n",
            "~~~ math\n" + r"312-\text{555}-1234" + "\n~~~\n",
            "``` {.math}\n" + r"\text{git}\text{hub.com/owner}" + "\n```\n",
        )
        for text in cases:
            with self.subTest(text=text):
                with self.assertRaises(PublicationExportError) as context:
                    validate_snapshot(
                        [SnapshotFile("README.md", text.encode("utf-8"), "0" * 64)]
                    )
                self.assertEqual(
                    "SNAPSHOT_MATH_FENCE_FORBIDDEN", context.exception.code
                )

    def test_rejects_excessive_or_malformed_link_nesting(self) -> None:
        nested = "[x](README.md)"
        for _ in range(export_publication.MAX_MARKDOWN_LINK_NESTING + 2):
            nested = f"[{nested}](README.md)"
        with self.assertRaises(PublicationExportError) as nesting_context:
            validate_snapshot(
                [SnapshotFile("README.md", nested.encode("utf-8"), "0" * 64)]
            )
        self.assertEqual(
            "SNAPSHOT_LINK_NESTING_FORBIDDEN", nesting_context.exception.code
        )

        with self.assertRaises(PublicationExportError) as malformed_context:
            validate_snapshot([SnapshotFile("README.md", b"[" * 8_000, "0" * 64)])
        self.assertEqual(
            "SNAPSHOT_MALFORMED_LINK_FORBIDDEN", malformed_context.exception.code
        )

    def test_rejects_unapproved_raw_html_resources(self) -> None:
        cases = (
            '<video poster="https://tracker.invalid/poster.png"></video>\n',
            '<object data="https://tracker.invalid/object.bin"></object>\n',
            '<embed src="https://tracker.invalid/embed.bin">\n',
            '<track src="https://tracker.invalid/captions.vtt">\n',
            '<svg><image href="https://tracker.invalid/image.png"></image></svg>\n',
            '<img/src="https://tracker.invalid/image.png">\n',
            '<video/poster="https://tracker.invalid/poster.png">\n',
            '<object/data="https://tracker.invalid/object.bin">\n',
            "<svg/onload=\"fetch('https://tracker.invalid/pixel')\">\n",
        )
        for text in cases:
            with self.subTest(text=text):
                with self.assertRaises(PublicationExportError) as context:
                    validate_snapshot(
                        [SnapshotFile("README.md", text.encode("utf-8"), "0" * 64)]
                    )
                self.assertEqual("SNAPSHOT_RAW_HTML_FORBIDDEN", context.exception.code)

    def test_allows_only_stable_anchor_and_line_break_html(self) -> None:
        text = (
            '<a id="course-map"></a>\n'
            "First line<br>Second line<br />Third line\n"
            '`<video poster="https://example.org/poster.png"></video>`\n'
            '```html\n<object data="https://example.org/file"></object>\n```\n'
        )
        validate_snapshot([SnapshotFile("README.md", text.encode("utf-8"), "0" * 64)])

    def test_rejects_empty_markdown_target_with_controlled_error(self) -> None:
        for text, expected_code in (
            ("[]()\n", "SNAPSHOT_EMPTY_LINK_TARGET_FORBIDDEN"),
            ("![]()\n", "SNAPSHOT_MARKDOWN_IMAGE_FORBIDDEN"),
        ):
            with self.subTest(text=text):
                with self.assertRaises(PublicationExportError) as context:
                    validate_snapshot(
                        [SnapshotFile("README.md", text.encode("utf-8"), "0" * 64)]
                    )
                self.assertEqual(expected_code, context.exception.code)


class ExportIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def committed_repo(
        self, files: Mapping[str, str | bytes] | None = None
    ) -> TemporaryGitRepository:
        repo = create_repository(self.base / "repo")
        for path, data in (files or valid_files()).items():
            repo.write(path, data)
        repo.commit()
        return repo

    def test_exports_only_manifest_files_without_git_identity(self) -> None:
        files = valid_files()
        files["private-source.md"] = "Not on the publication list.\n"
        repo = self.committed_repo(files)
        output = self.base / "public"

        report = export_snapshot(repo.root, output)

        exported = sorted(
            path.relative_to(output).as_posix()
            for path in output.rglob("*")
            if path.is_file()
        )
        self.assertEqual(
            sorted([*valid_files(), GENERATED_MANIFEST, CHECKSUMS_FILE]),
            exported,
        )
        self.assertFalse((output / ".git").exists())
        all_bytes = b"".join(
            path.read_bytes() for path in output.rglob("*") if path.is_file()
        )
        self.assertNotIn(("Canary " + "Personal Name").encode(), all_bytes)
        self.assertNotIn(("canary" + "@" + "example.invalid").encode(), all_bytes)
        self.assertEqual(3, report.content_count)

        generated = json.loads(
            (output / GENERATED_MANIFEST).read_text(encoding="utf-8")
        )
        self.assertNotIn("commit", generated)
        self.assertNotIn("remote", generated)
        self.assertNotIn("created_at", generated)

    def test_rejects_dirty_or_untracked_release_checkout(self) -> None:
        repo = self.committed_repo()
        repo.write("README.md", "Uncommitted private replacement.\n")
        repo.write("untracked.md", "Untracked draft.\n")
        output = self.base / "public"

        with self.assertRaises(PublicationExportError) as context:
            export_snapshot(repo.root, output)

        self.assertEqual("SOURCE_CHECKOUT_NOT_CLEAN", context.exception.code)
        self.assertFalse(output.exists())

    def test_rejects_source_ref_that_is_not_checked_out(self) -> None:
        repo = self.committed_repo()
        original_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        repo.write("README.md", "# Updated home | 更新后的首页\n")
        repo.commit()
        output = self.base / "public"

        with self.assertRaises(PublicationExportError) as context:
            export_snapshot(repo.root, output, original_commit)

        self.assertEqual("SOURCE_REF_NOT_CHECKED_OUT", context.exception.code)
        self.assertFalse(output.exists())

    def test_ignores_replace_refs_and_inherited_git_environment(self) -> None:
        repo = self.committed_repo()
        original_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        repo.write("README.md", "Replacement commit content.\n")
        repo.commit()
        replacement_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        repo.run("replace", original_commit, replacement_commit)
        repo.run("--no-replace-objects", "checkout", "--detach", original_commit)

        replace_output = self.base / "replace-output"
        export_snapshot(repo.root, replace_output, original_commit)
        self.assertEqual(
            valid_files()["README.md"],
            (replace_output / "README.md").read_text(encoding="utf-8"),
        )

        environment_output = self.base / "environment-output"
        with patch.dict(os.environ, {"GIT_DIR": str(self.base / "missing-git-dir")}):
            export_snapshot(repo.root, environment_output, original_commit)
        self.assertEqual(
            valid_files()["README.md"],
            (environment_output / "README.md").read_text(encoding="utf-8"),
        )

    def test_git_reads_are_offline_and_noninteractive(self) -> None:
        repo = self.committed_repo()
        output = self.base / "public"
        real_run = subprocess.run

        with patch(
            "scripts.export_publication.subprocess.run", wraps=real_run
        ) as mocked_run:
            export_snapshot(repo.root, output)

        self.assertGreater(len(mocked_run.call_args_list), 0)
        for call in mocked_run.call_args_list:
            environment = call.kwargs["env"]
            self.assertEqual("1", environment["GIT_NO_LAZY_FETCH"])
            self.assertEqual("0", environment["GIT_TERMINAL_PROMPT"])
            self.assertEqual(subprocess.DEVNULL, call.kwargs["stdin"])
        ls_tree_commands = [
            call.args[0]
            for call in mocked_run.call_args_list
            if "ls-tree" in call.args[0]
        ]
        self.assertGreaterEqual(len(ls_tree_commands), 2)
        for command in ls_tree_commands:
            self.assertIn("--literal-pathspecs", command)
            self.assertNotIn("-r", command)

    def test_rejects_symlink_and_leaves_no_output(self) -> None:
        repo = create_repository(self.base / "repo")
        repo.write("README.md", "# Home | 首页\n")
        repo.write(
            MANIFEST_PATH,
            manifest_text(MANIFEST_PATH, "README.md", "docs/link.md"),
        )
        (repo.root / "docs").mkdir()
        os.symlink("../README.md", repo.root / "docs/link.md")
        repo.commit()
        output = self.base / "public"

        with self.assertRaises(PublicationExportError) as context:
            export_snapshot(repo.root, output)

        self.assertEqual("SNAPSHOT_SPECIAL_FILE_FORBIDDEN", context.exception.code)
        self.assertFalse(output.exists())

    def test_rejects_link_outside_allowlist(self) -> None:
        files = valid_files()
        files["README.md"] = "[Private](private-source.md)\n"
        files["private-source.md"] = "Private source.\n"
        repo = self.committed_repo(files)
        output = self.base / "public"

        with self.assertRaises(PublicationExportError) as context:
            export_snapshot(repo.root, output)

        self.assertEqual("SNAPSHOT_LINK_OUTSIDE_ALLOWLIST", context.exception.code)
        self.assertFalse(output.exists())

    def test_rejects_binary_and_lfs_pointer(self) -> None:
        for name, data, expected_code in (
            ("binary", b"bad\x00data", "SNAPSHOT_BINARY_FORBIDDEN"),
            (
                "lfs",
                ("version https://git-lfs." + "github.com/spec/v1\n").encode(),
                "SNAPSHOT_LFS_POINTER_FORBIDDEN",
            ),
        ):
            with self.subTest(name=name):
                case_root = self.base / name
                repo = create_repository(case_root / "repo")
                repo.write("README.md", data)
                repo.write(MANIFEST_PATH, manifest_text(MANIFEST_PATH, "README.md"))
                repo.commit()
                with self.assertRaises(PublicationExportError) as context:
                    export_snapshot(repo.root, case_root / "public")
                self.assertEqual(expected_code, context.exception.code)

    def test_does_not_overwrite_existing_output(self) -> None:
        repo = self.committed_repo()
        output = self.base / "public"
        output.mkdir()
        marker = output / "keep.txt"
        marker.write_text("keep", encoding="utf-8")

        with self.assertRaises(PublicationExportError) as context:
            export_snapshot(repo.root, output)

        self.assertEqual("OUTPUT_ALREADY_EXISTS", context.exception.code)
        self.assertEqual("keep", marker.read_text(encoding="utf-8"))

    def test_does_not_replace_output_created_during_export(self) -> None:
        repo = self.committed_repo()
        output = self.base / "public"

        def create_racing_output(_repo_root: Path, output_dir: Path) -> None:
            output_dir.mkdir()

        with patch.object(
            export_publication,
            "_assert_output_location",
            side_effect=create_racing_output,
        ), self.assertRaises(PublicationExportError):
            export_snapshot(repo.root, output)

        self.assertTrue(output.is_dir())
        self.assertEqual([], list(output.iterdir()))

    def test_wraps_output_io_error_and_removes_partial_artifact(self) -> None:
        repo = self.committed_repo()
        output = self.base / "public"
        with patch.object(
            export_publication,
            "_write_regular_file",
            side_effect=PermissionError("/sensitive/path"),
        ), self.assertRaises(PublicationExportError) as context:
            export_snapshot(repo.root, output)

        self.assertEqual("OUTPUT_IO_FAILED", context.exception.code)
        self.assertFalse(output.exists())

    def test_same_commit_produces_identical_bytes(self) -> None:
        repo = self.committed_repo()
        first = self.base / "first"
        second = self.base / "second"

        first_report = export_snapshot(repo.root, first)
        second_report = export_snapshot(repo.root, second)

        first_files = {
            path.relative_to(first).as_posix(): path.read_bytes()
            for path in first.rglob("*")
            if path.is_file()
        }
        second_files = {
            path.relative_to(second).as_posix(): path.read_bytes()
            for path in second.rglob("*")
            if path.is_file()
        }
        self.assertEqual(first_files, second_files)
        self.assertEqual(first_report, second_report)

    def test_verifies_export_without_reading_repository(self) -> None:
        repo = self.committed_repo()
        output = self.base / "public"
        export_report = export_snapshot(repo.root, output)

        verification_report = verify_snapshot(output, export_report.content_set_sha256)

        self.assertEqual(export_report, verification_report)

    def test_verification_rejects_tampering_and_extra_git_directory(self) -> None:
        for name, mutate, expected_code in (
            (
                "tampered",
                lambda output: write_export_text(
                    output / "README.md", "Changed after export.\n"
                ),
                "ARTIFACT_EXPECTED_DIGEST_MISMATCH",
            ),
            (
                "git-metadata",
                lambda output: (output / ".git").mkdir(),
                "ARTIFACT_GIT_METADATA_FORBIDDEN",
            ),
            (
                "symlink",
                lambda output: os.symlink("README.md", output / "linked.md"),
                "ARTIFACT_SYMLINK_FORBIDDEN",
            ),
        ):
            with self.subTest(name=name):
                case_root = self.base / name
                case_root.mkdir()
                repo = create_repository(case_root / "repo")
                for path, data in valid_files().items():
                    repo.write(path, data)
                repo.commit()
                output = case_root / "public"
                export_report = export_snapshot(repo.root, output)
                mutate(output)

                with self.assertRaises(PublicationExportError) as context:
                    verify_snapshot(output, export_report.content_set_sha256)

                self.assertEqual(expected_code, context.exception.code)

    @unittest.skipUnless(os.name == "posix", "POSIX permission semantics required")
    def test_verification_rejects_unreadable_extra_directory(self) -> None:
        repo = self.committed_repo()
        output = self.base / "public"
        export_report = export_snapshot(repo.root, output)
        unreadable = output / "unreadable"
        unreadable.mkdir()
        (unreadable / "private.md").write_text("Hidden extra file.\n", encoding="utf-8")
        unreadable.chmod(0)
        try:
            with self.assertRaises(PublicationExportError):
                verify_snapshot(output, export_report.content_set_sha256)
        finally:
            unreadable.chmod(0o755)

    def test_verification_rejects_changed_root_directory_or_file_mtime(self) -> None:
        cases = (
            ("root", Path("."), "ARTIFACT_DIRECTORY_MTIME_INVALID"),
            (
                "directory",
                Path("docs"),
                "ARTIFACT_DIRECTORY_MTIME_INVALID",
            ),
            (
                "file",
                Path("README.md"),
                "ARTIFACT_FILE_MTIME_INVALID",
            ),
        )
        for name, target_path, expected_code in cases:
            with self.subTest(name=name):
                case_root = self.base / f"mtime-{name}"
                case_root.mkdir()
                repo = create_repository(case_root / "repo")
                for path, data in valid_files().items():
                    repo.write(path, data)
                repo.commit()
                output = case_root / "public"
                export_report = export_snapshot(repo.root, output)
                os.utime(output / target_path, (1_704_186_240, 1_704_186_240))

                with self.assertRaises(PublicationExportError) as context:
                    verify_snapshot(output, export_report.content_set_sha256)

                self.assertEqual(expected_code, context.exception.code)

    def test_verification_bounds_artifact_enumeration(self) -> None:
        repo = self.committed_repo()
        output = self.base / "public"
        export_report = export_snapshot(repo.root, output)

        with patch.object(export_publication, "MAX_ARTIFACT_ENTRIES", 1):
            with self.assertRaises(PublicationExportError) as context:
                verify_snapshot(output, export_report.content_set_sha256)

        self.assertEqual("ARTIFACT_ENTRY_COUNT_INVALID", context.exception.code)

    def test_verification_rejects_fully_recomputed_tampered_metadata(self) -> None:
        repo = self.committed_repo()
        output = self.base / "public"
        export_report = export_snapshot(repo.root, output)
        write_export_text(
            output / "README.md",
            "# Replaced public content | 已替换的公开内容\n",
        )
        content_files: list[SnapshotFile] = []
        for file_path in sorted(valid_files()):
            data = (output / file_path).read_bytes()
            content_files.append(
                SnapshotFile(file_path, data, hashlib.sha256(data).hexdigest())
            )
        manifest_bytes, checksum_bytes, _digest = generated_metadata(content_files)
        (output / GENERATED_MANIFEST).write_bytes(manifest_bytes)
        (output / CHECKSUMS_FILE).write_bytes(checksum_bytes)
        for path in (output / GENERATED_MANIFEST, output / CHECKSUMS_FILE):
            os.utime(
                path,
                (
                    export_publication.SOURCE_DATE_EPOCH,
                    export_publication.SOURCE_DATE_EPOCH,
                ),
            )

        with self.assertRaises(PublicationExportError) as context:
            verify_snapshot(output, export_report.content_set_sha256)

        self.assertEqual("ARTIFACT_EXPECTED_DIGEST_MISMATCH", context.exception.code)

    def test_rejects_oversized_blob_before_reading_blob_content(self) -> None:
        files = valid_files()
        files["README.md"] = "x" * (export_publication.MAX_FILE_BYTES + 1)
        repo = self.committed_repo(files)

        with self.assertRaises(PublicationExportError) as context:
            export_snapshot(repo.root, self.base / "public")

        self.assertEqual("SNAPSHOT_FILE_TOO_LARGE", context.exception.code)

    def test_cli_redacts_unexpected_internal_error(self) -> None:
        standard_output = io.StringIO()
        standard_error = io.StringIO()
        arguments = [
            "export_publication.py",
            "export",
            "--output",
            str(self.base / "public"),
        ]
        with (
            patch.object(sys, "argv", arguments),
            patch.object(
                export_publication,
                "export_snapshot",
                side_effect=ValueError("/sensitive/local/path"),
            ),
            redirect_stdout(standard_output),
            redirect_stderr(standard_error),
        ):
            exit_code = export_publication.main()

        self.assertEqual(1, exit_code)
        self.assertEqual(
            "error_code=INTERNAL_ERROR\npublication_export=FAIL\n",
            standard_output.getvalue(),
        )
        self.assertEqual("", standard_error.getvalue())


if __name__ == "__main__":
    unittest.main()
