from __future__ import annotations

import io
import os
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import package_offline_site
from scripts.package_offline_site import (
    OfflinePackageError,
    create_offline_package,
    verify_offline_package,
)
from tests.test_build_static_site import create_snapshot


class OfflinePackageIntegrationTests(unittest.TestCase):
    def test_creates_portable_package_with_only_static_site_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            output = root / "project-covenant-offline.zip"
            snapshot.mkdir()
            digest = create_snapshot(snapshot)

            report = create_offline_package(snapshot, digest, output)

            self.assertEqual(2, report.page_count)
            self.assertEqual(3, report.site_file_count)
            self.assertEqual(report.package_bytes, output.stat().st_size)
            self.assertEqual(64, len(report.package_sha256))
            with zipfile.ZipFile(output) as archive:
                infos = archive.infolist()
                self.assertEqual(
                    {
                        "project-covenant-offline/assets/site.css",
                        "project-covenant-offline/docs/guide.html",
                        "project-covenant-offline/index.html",
                    },
                    {info.filename for info in infos},
                )
                self.assertTrue(all(not info.is_dir() for info in infos))
                self.assertTrue(
                    all(info.compress_type == zipfile.ZIP_STORED for info in infos)
                )
                self.assertTrue(
                    all(info.date_time == package_offline_site.PACKAGE_TIMESTAMP for info in infos)
                )
                self.assertNotIn(
                    b"publication/site-content.txt",
                    b"".join(archive.read(info) for info in infos),
                )

            verified = verify_offline_package(snapshot, digest, output)
            self.assertEqual(report, verified)

    def test_same_snapshot_produces_identical_package_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            first = root / "first.zip"
            second = root / "second.zip"
            snapshot.mkdir()
            digest = create_snapshot(snapshot)

            first_report = create_offline_package(snapshot, digest, first)
            second_report = create_offline_package(snapshot, digest, second)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first_report.package_sha256, second_report.package_sha256)

    def test_rejects_overwrite_inside_snapshot_symlink_and_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            output = root / "offline.zip"
            snapshot.mkdir()
            digest = create_snapshot(snapshot)
            create_offline_package(snapshot, digest, output)

            with self.assertRaises(OfflinePackageError) as context:
                create_offline_package(snapshot, digest, output)
            self.assertEqual("PACKAGE_OUTPUT_ALREADY_EXISTS", context.exception.code)

            with self.assertRaises(OfflinePackageError) as context:
                create_offline_package(snapshot, digest, snapshot / "inside.zip")
            self.assertEqual("PACKAGE_OUTPUT_INSIDE_SNAPSHOT", context.exception.code)

            symlink = root / "link.zip"
            symlink.symlink_to(output)
            with self.assertRaises(OfflinePackageError):
                verify_offline_package(snapshot, digest, symlink)

            tampered = bytearray(output.read_bytes())
            tampered[len(tampered) // 2] ^= 1
            output.write_bytes(tampered)
            with self.assertRaises(OfflinePackageError) as context:
                verify_offline_package(snapshot, digest, output)
            self.assertEqual("PACKAGE_CONTENT_MISMATCH", context.exception.code)

    def test_failed_create_removes_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            output = root / "offline.zip"
            snapshot.mkdir()
            digest = create_snapshot(snapshot)

            with (
                patch.object(
                    package_offline_site,
                    "_verify_staging_descriptor",
                    side_effect=OfflinePackageError("PACKAGE_STAGING_CHANGED"),
                ),
                self.assertRaises(OfflinePackageError),
            ):
                create_offline_package(snapshot, digest, output)

            self.assertFalse(output.exists())
            self.assertFalse(
                any(
                    path.name.startswith(package_offline_site.STAGING_PREFIX)
                    for path in root.iterdir()
                )
            )

    def test_write_failure_removes_new_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            output = root / "offline.zip"
            snapshot.mkdir()
            digest = create_snapshot(snapshot)

            with (
                patch.object(package_offline_site.os, "write", side_effect=OSError),
                self.assertRaises(OfflinePackageError) as context,
            ):
                create_offline_package(snapshot, digest, output)

            self.assertEqual("PACKAGE_OUTPUT_WRITE_FAILED", context.exception.code)
            self.assertFalse(output.exists())

    def test_cleanup_refuses_to_delete_replaced_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            output = root / "offline.zip"
            snapshot.mkdir()
            digest = create_snapshot(snapshot)
            replacement = b"replacement owned by another writer"
            original_publish = package_offline_site._publish_staging

            def replace_then_publish(
                parent_descriptor: int,
                staging_name: str,
                output_name: str,
                identity: tuple[int, int],
                expected_size: int,
            ) -> None:
                output.write_bytes(replacement)
                original_publish(
                    parent_descriptor,
                    staging_name,
                    output_name,
                    identity,
                    expected_size,
                )

            with (
                patch.object(
                    package_offline_site,
                    "_publish_staging",
                    side_effect=replace_then_publish,
                ),
                self.assertRaises(OfflinePackageError) as context,
            ):
                create_offline_package(snapshot, digest, output)

            self.assertEqual("PACKAGE_OUTPUT_ALREADY_EXISTS", context.exception.code)
            self.assertEqual(replacement, output.read_bytes())
            self.assertFalse(
                any(
                    candidate.name.startswith(package_offline_site.STAGING_PREFIX)
                    for candidate in root.iterdir()
                )
            )

    def test_open_parent_descriptor_prevents_symlink_redirection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            checked_parent = root / "checked-parent"
            moved_parent = root / "checked-parent-old"
            redirect = root / "redirect"
            output = checked_parent / "offline.zip"
            snapshot.mkdir()
            checked_parent.mkdir()
            redirect.mkdir()
            digest = create_snapshot(snapshot)
            original_load = package_offline_site._load_site_files

            def swap_parent_then_load(
                snapshot_dir: Path, expected_digest: str
            ) -> tuple[dict[str, bytes], int]:
                checked_parent.rename(moved_parent)
                checked_parent.symlink_to(redirect, target_is_directory=True)
                return original_load(snapshot_dir, expected_digest)

            with (
                patch.object(
                    package_offline_site,
                    "_load_site_files",
                    side_effect=swap_parent_then_load,
                ),
                self.assertRaises(OfflinePackageError) as context,
            ):
                create_offline_package(snapshot, digest, output)

            self.assertEqual("PACKAGE_OUTPUT_PARENT_CHANGED", context.exception.code)
            self.assertFalse((redirect / "offline.zip").exists())
            self.assertFalse((moved_parent / "offline.zip").exists())
            self.assertEqual([], list(moved_parent.iterdir()))


class OfflinePackageCliTests(unittest.TestCase):
    def test_cli_reports_fixed_error_without_path_or_traceback(self) -> None:
        stream = io.StringIO()
        arguments = [
            "package_offline_site.py",
            "verify",
            "--snapshot",
            "/private/snapshot",
            "--expected-content-set-sha256",
            "0" * 64,
            "--input",
            "/private/offline.zip",
        ]
        with (
            patch.object(os, "name", "posix"),
            patch.object(
                package_offline_site,
                "verify_offline_package",
                side_effect=OfflinePackageError("PACKAGE_CONTENT_MISMATCH"),
            ),
            patch.object(package_offline_site.sys, "argv", arguments),
            redirect_stdout(stream),
        ):
            result = package_offline_site.main()

        text = stream.getvalue()
        self.assertEqual(1, result)
        self.assertIn("error_code=PACKAGE_CONTENT_MISMATCH", text)
        self.assertIn("offline_package_verify=FAIL", text)
        self.assertNotIn("/private", text)
        self.assertNotIn("Traceback", text)
