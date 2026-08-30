#!/usr/bin/env python3
"""Create and verify a deterministic, portable offline reading package."""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import re
import secrets
import stat
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts import build_static_site
elif __package__:
    from . import build_static_site
else:
    import build_static_site


PACKAGE_ROOT = "project-covenant-offline"
PACKAGE_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
MAX_PACKAGE_BYTES = build_static_site.MAX_SITE_TOTAL_BYTES + 8 * 1024 * 1024
CONTROL = re.compile(r"[\x00-\x1f\x7f]")
STAGING_ATTEMPTS = 16
STAGING_PREFIX = ".project-covenant-offline-staging-"

ParentIdentity = tuple[int, int, int]
InodeIdentity = tuple[int, int]


class OfflinePackageError(RuntimeError):
    """A fail-closed package error whose code contains no private path or data."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class OfflinePackageReport:
    page_count: int
    site_file_count: int
    package_bytes: int
    package_sha256: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_site_files(
    snapshot_dir: Path, expected_content_set_sha256: str
) -> tuple[dict[str, bytes], int]:
    try:
        return build_static_site._load_expected_site(  # noqa: SLF001
            snapshot_dir, expected_content_set_sha256
        )
    except build_static_site.SiteBuildError as error:
        raise OfflinePackageError(f"SOURCE_{error.code}") from error


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(
        filename=f"{PACKAGE_ROOT}/{path}",
        date_time=PACKAGE_TIMESTAMP,
    )
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.internal_attr = 0
    info.extra = b""
    info.comment = b""
    return info


def _expected_package_bytes(site_files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    try:
        with zipfile.ZipFile(
            buffer,
            mode="w",
            compression=zipfile.ZIP_STORED,
            allowZip64=False,
            strict_timestamps=True,
        ) as archive:
            archive.comment = b""
            for path, data in sorted(site_files.items()):
                archive.writestr(_zip_info(path), data)
    except (OSError, RuntimeError, ValueError, zipfile.LargeZipFile) as error:
        raise OfflinePackageError("PACKAGE_ENCODING_FAILED") from error
    package = buffer.getvalue()
    if not package or len(package) > MAX_PACKAGE_BYTES:
        raise OfflinePackageError("PACKAGE_SIZE_INVALID")
    return package


def _parent_identity(details: os.stat_result) -> ParentIdentity:
    return details.st_dev, details.st_ino, details.st_mode


def _inode_identity(details: os.stat_result) -> InodeIdentity:
    return details.st_dev, details.st_ino


def _read_parent_identity(parent: Path, error_code: str) -> ParentIdentity:
    try:
        details = parent.lstat()
    except OSError as error:
        raise OfflinePackageError(error_code) from error
    if stat.S_ISLNK(details.st_mode) or not stat.S_ISDIR(details.st_mode):
        raise OfflinePackageError(error_code)
    return _parent_identity(details)


def _assert_output_location(
    snapshot_dir: Path, output_file: Path
) -> ParentIdentity:
    if (
        not output_file.name
        or output_file.suffix.casefold() != ".zip"
        or output_file.name.casefold() == ".git"
        or CONTROL.search(output_file.name)
    ):
        raise OfflinePackageError("PACKAGE_OUTPUT_NAME_INVALID")
    parent = output_file.parent
    expected_parent = _read_parent_identity(parent, "PACKAGE_OUTPUT_PARENT_INVALID")
    try:
        resolved_snapshot = snapshot_dir.resolve()
        resolved_output = output_file.resolve(strict=False)
    except OSError as error:
        raise OfflinePackageError("PACKAGE_OUTPUT_LOCATION_INVALID") from error
    if (
        _read_parent_identity(parent, "PACKAGE_OUTPUT_PARENT_CHANGED")
        != expected_parent
    ):
        raise OfflinePackageError("PACKAGE_OUTPUT_PARENT_CHANGED")
    try:
        resolved_output.relative_to(resolved_snapshot)
    except ValueError:
        return expected_parent
    raise OfflinePackageError("PACKAGE_OUTPUT_INSIDE_SNAPSHOT")


def _require_create_platform() -> None:
    required_flags = ("O_DIRECTORY", "O_NOFOLLOW")
    if (
        os.name != "posix"
        or any(not hasattr(os, name) for name in required_flags)
        or os.open not in os.supports_dir_fd
        or os.stat not in os.supports_dir_fd
        or os.stat not in os.supports_follow_symlinks
        or os.unlink not in os.supports_dir_fd
        or os.link not in os.supports_dir_fd
        or os.link not in os.supports_follow_symlinks
    ):
        raise OfflinePackageError("PACKAGE_PLATFORM_UNSUPPORTED")


def _open_output_parent(
    parent: Path, expected_identity: ParentIdentity
) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    flags |= getattr(os, "O_CLOEXEC", 0)
    descriptor: int | None = None
    try:
        descriptor = os.open(parent, flags)
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISDIR(opened.st_mode)
            or _parent_identity(opened) != expected_identity
            or _read_parent_identity(parent, "PACKAGE_OUTPUT_PARENT_CHANGED")
            != expected_identity
        ):
            raise OfflinePackageError("PACKAGE_OUTPUT_PARENT_CHANGED")
        return descriptor
    except OfflinePackageError:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise
    except OSError as error:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise OfflinePackageError("PACKAGE_OUTPUT_PARENT_OPEN_FAILED") from error


def _assert_parent_unchanged(
    parent: Path, expected_identity: ParentIdentity
) -> None:
    if (
        _read_parent_identity(parent, "PACKAGE_OUTPUT_PARENT_CHANGED")
        != expected_identity
    ):
        raise OfflinePackageError("PACKAGE_OUTPUT_PARENT_CHANGED")


def _assert_output_absent(parent_descriptor: int, output_name: str) -> None:
    try:
        os.stat(output_name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError as error:
        raise OfflinePackageError("PACKAGE_OUTPUT_STATUS_FAILED") from error
    raise OfflinePackageError("PACKAGE_OUTPUT_ALREADY_EXISTS")


def _open_private_staging(parent_descriptor: int) -> tuple[str, int, InodeIdentity]:
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    flags |= getattr(os, "O_CLOEXEC", 0)
    for _ in range(STAGING_ATTEMPTS):
        name = f"{STAGING_PREFIX}{secrets.token_hex(16)}"
        try:
            descriptor = os.open(name, flags, 0o600, dir_fd=parent_descriptor)
        except FileExistsError:
            continue
        except OSError as error:
            raise OfflinePackageError("PACKAGE_STAGING_CREATE_FAILED") from error
        try:
            opened = os.fstat(descriptor)
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_nlink != 1
                or stat.S_IMODE(opened.st_mode) != 0o600
            ):
                raise OfflinePackageError("PACKAGE_STAGING_INVALID")
            return name, descriptor, _inode_identity(opened)
        except OfflinePackageError:
            try:
                os.close(descriptor)
            except OSError:
                pass
            try:
                os.unlink(name, dir_fd=parent_descriptor)
            except OSError:
                pass
            raise
        except OSError as error:
            try:
                os.close(descriptor)
            except OSError:
                pass
            try:
                os.unlink(name, dir_fd=parent_descriptor)
            except OSError:
                pass
            raise OfflinePackageError("PACKAGE_STAGING_CREATE_FAILED") from error
    raise OfflinePackageError("PACKAGE_STAGING_CREATE_FAILED")


def _write_staging_descriptor(descriptor: int, data: bytes) -> None:
    try:
        view = memoryview(data)
        written = 0
        while written < len(view):
            count = os.write(descriptor, view[written:])
            if count <= 0:
                raise OfflinePackageError("PACKAGE_OUTPUT_WRITE_FAILED")
            written += count
        os.fchmod(descriptor, 0o644)
        os.fsync(descriptor)
    except OfflinePackageError:
        raise
    except OSError as error:
        raise OfflinePackageError("PACKAGE_OUTPUT_WRITE_FAILED") from error


def _verify_staging_descriptor(
    descriptor: int, expected: bytes, identity: InodeIdentity
) -> None:
    try:
        os.lseek(descriptor, 0, os.SEEK_SET)
        before = os.fstat(descriptor)
        if (
            _inode_identity(before) != identity
            or not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o644
            or before.st_size != len(expected)
        ):
            raise OfflinePackageError("PACKAGE_STAGING_CHANGED")
        chunks: list[bytes] = []
        remaining = len(expected)
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                raise OfflinePackageError("PACKAGE_STAGING_CHANGED")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise OfflinePackageError("PACKAGE_STAGING_CHANGED")
        after = os.fstat(descriptor)
        before_state = (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_nlink,
            before.st_size,
            before.st_mtime_ns,
        )
        after_state = (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_nlink,
            after.st_size,
            after.st_mtime_ns,
        )
        if before_state != after_state:
            raise OfflinePackageError("PACKAGE_STAGING_CHANGED")
        if b"".join(chunks) != expected:
            raise OfflinePackageError("PACKAGE_CONTENT_MISMATCH")
    except OfflinePackageError:
        raise
    except OSError as error:
        raise OfflinePackageError("PACKAGE_STAGING_VERIFY_FAILED") from error


def _cleanup_staging(
    parent_descriptor: int, staging_name: str, identity: InodeIdentity
) -> None:
    try:
        details = os.stat(
            staging_name, dir_fd=parent_descriptor, follow_symlinks=False
        )
    except FileNotFoundError:
        return
    except OSError as error:
        raise OfflinePackageError("PACKAGE_STAGING_CLEANUP_FAILED") from error
    if _inode_identity(details) != identity or not stat.S_ISREG(details.st_mode):
        raise OfflinePackageError("PACKAGE_STAGING_CHANGED")
    try:
        os.unlink(staging_name, dir_fd=parent_descriptor)
    except FileNotFoundError:
        return
    except OSError as error:
        raise OfflinePackageError("PACKAGE_STAGING_CLEANUP_FAILED") from error


def _publish_staging(
    parent_descriptor: int,
    staging_name: str,
    output_name: str,
    identity: InodeIdentity,
    expected_size: int,
) -> None:
    try:
        os.link(
            staging_name,
            output_name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
    except FileExistsError as error:
        raise OfflinePackageError("PACKAGE_OUTPUT_ALREADY_EXISTS") from error
    except OSError as error:
        raise OfflinePackageError("PACKAGE_OUTPUT_PUBLISH_FAILED") from error
    try:
        details = os.stat(
            output_name, dir_fd=parent_descriptor, follow_symlinks=False
        )
        if (
            _inode_identity(details) != identity
            or not stat.S_ISREG(details.st_mode)
            or stat.S_IMODE(details.st_mode) != 0o644
            or details.st_size != expected_size
        ):
            raise OfflinePackageError("PACKAGE_OUTPUT_CHANGED")
    except OfflinePackageError:
        raise
    except OSError as error:
        raise OfflinePackageError("PACKAGE_OUTPUT_STATUS_FAILED") from error


def _write_new_package(
    parent_descriptor: int,
    parent: Path,
    parent_identity: ParentIdentity,
    output_name: str,
    data: bytes,
) -> None:
    staging_name, staging_descriptor, staging_identity = _open_private_staging(
        parent_descriptor
    )
    staging_present = True
    try:
        _write_staging_descriptor(staging_descriptor, data)
        _verify_staging_descriptor(staging_descriptor, data, staging_identity)
        _assert_parent_unchanged(parent, parent_identity)
        _assert_output_absent(parent_descriptor, output_name)
        _publish_staging(
            parent_descriptor,
            staging_name,
            output_name,
            staging_identity,
            len(data),
        )
        # The public name is never removed after this point. Cleanup is limited to
        # the random staging name anchored beneath the already-open parent fd.
        _cleanup_staging(parent_descriptor, staging_name, staging_identity)
        staging_present = False
        _assert_parent_unchanged(parent, parent_identity)
        final = os.stat(
            output_name, dir_fd=parent_descriptor, follow_symlinks=False
        )
        if (
            _inode_identity(final) != staging_identity
            or not stat.S_ISREG(final.st_mode)
            or final.st_nlink != 1
            or stat.S_IMODE(final.st_mode) != 0o644
            or final.st_size != len(data)
        ):
            raise OfflinePackageError("PACKAGE_OUTPUT_CHANGED")
    except OfflinePackageError:
        raise
    except OSError as error:
        raise OfflinePackageError("PACKAGE_OUTPUT_STATUS_FAILED") from error
    finally:
        try:
            os.close(staging_descriptor)
        except OSError:
            pass
        if staging_present:
            _cleanup_staging(parent_descriptor, staging_name, staging_identity)


def _read_regular_package(input_file: Path) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    try:
        descriptor = os.open(input_file, flags)
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise OfflinePackageError("PACKAGE_INPUT_NOT_REGULAR")
        if before.st_size <= 0 or before.st_size > MAX_PACKAGE_BYTES:
            raise OfflinePackageError("PACKAGE_INPUT_SIZE_INVALID")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                raise OfflinePackageError("PACKAGE_INPUT_CHANGED")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise OfflinePackageError("PACKAGE_INPUT_CHANGED")
        after = os.fstat(descriptor)
        identity_before = (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_size,
            before.st_mtime_ns,
        )
        identity_after = (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_size,
            after.st_mtime_ns,
        )
        if identity_before != identity_after:
            raise OfflinePackageError("PACKAGE_INPUT_CHANGED")
        return b"".join(chunks)
    except OfflinePackageError:
        raise
    except OSError as error:
        raise OfflinePackageError("PACKAGE_INPUT_READ_FAILED") from error
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError as error:
                raise OfflinePackageError("PACKAGE_INPUT_CLOSE_FAILED") from error


def _report(package: bytes, page_count: int, site_file_count: int) -> OfflinePackageReport:
    return OfflinePackageReport(
        page_count=page_count,
        site_file_count=site_file_count,
        package_bytes=len(package),
        package_sha256=sha256_bytes(package),
    )


def create_offline_package(
    snapshot_dir: Path,
    expected_content_set_sha256: str,
    output_file: Path,
) -> OfflinePackageReport:
    _require_create_platform()
    parent_identity = _assert_output_location(snapshot_dir, output_file)
    parent = output_file.parent
    parent_descriptor = _open_output_parent(parent, parent_identity)
    try:
        _assert_output_absent(parent_descriptor, output_file.name)
        site_files, page_count = _load_site_files(
            snapshot_dir, expected_content_set_sha256
        )
        package = _expected_package_bytes(site_files)
        _assert_parent_unchanged(parent, parent_identity)
        _write_new_package(
            parent_descriptor,
            parent,
            parent_identity,
            output_file.name,
            package,
        )
        return _report(package, page_count, len(site_files))
    finally:
        try:
            os.close(parent_descriptor)
        except OSError:
            pass


def verify_offline_package(
    snapshot_dir: Path,
    expected_content_set_sha256: str,
    input_file: Path,
) -> OfflinePackageReport:
    if os.name != "posix":
        raise OfflinePackageError("PACKAGE_PLATFORM_UNSUPPORTED")
    site_files, page_count = _load_site_files(snapshot_dir, expected_content_set_sha256)
    expected = _expected_package_bytes(site_files)
    actual = _read_regular_package(input_file)
    if actual != expected:
        raise OfflinePackageError("PACKAGE_CONTENT_MISMATCH")
    return _report(expected, page_count, len(site_files))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or verify a deterministic Project Covenant offline ZIP."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    create_parser = subparsers.add_parser(
        "create", help="Create an offline ZIP from a verified publication snapshot."
    )
    create_parser.add_argument("--snapshot", required=True, type=Path)
    create_parser.add_argument("--expected-content-set-sha256", required=True)
    create_parser.add_argument("--output", required=True, type=Path)
    verify_parser = subparsers.add_parser(
        "verify", help="Verify an offline ZIP against its publication snapshot."
    )
    verify_parser.add_argument("--snapshot", required=True, type=Path)
    verify_parser.add_argument("--expected-content-set-sha256", required=True)
    verify_parser.add_argument("--input", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "create":
            report = create_offline_package(
                args.snapshot, args.expected_content_set_sha256, args.output
            )
        elif args.command == "verify":
            report = verify_offline_package(
                args.snapshot, args.expected_content_set_sha256, args.input
            )
        else:
            raise OfflinePackageError("PACKAGE_COMMAND_UNSUPPORTED")
    except OfflinePackageError as error:
        print(f"error_code={error.code}")
        print(f"offline_package_{args.command}=FAIL")
        return 1
    except Exception:
        print("error_code=INTERNAL_ERROR")
        print(f"offline_package_{args.command}=FAIL")
        return 1
    print(f"offline_package_pages={report.page_count}")
    print(f"offline_package_site_files={report.site_file_count}")
    print(f"offline_package_bytes={report.package_bytes}")
    print(f"offline_package_sha256={report.package_sha256}")
    print(f"offline_package_start={PACKAGE_ROOT}/index.html")
    print(f"offline_package_{args.command}=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
