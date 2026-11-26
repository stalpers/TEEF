"""Build the ZIP archive cases of the TEEF conformance suite.

Run from the repository root:

    python conformance/tools/build_archives.py

The script uses only the Python standard library. Output is deterministic:
entries are written in list order, stored without compression, with a fixed
timestamp and fixed permissions, so rebuilding unchanged cases produces
identical bytes.

Each case writes conformance/0.1.0/<case>/package.zip. The matching case.json
files are written by hand. Several archives are deliberately unsafe. They exist
only to test that recipients reject them. Do not extract them with tools that
follow paths or links.
"""
import hashlib
import io
import json
import pathlib
import stat
import warnings
import zipfile
from typing import NamedTuple

CASES = pathlib.Path(__file__).resolve().parent.parent / "0.1.0"
BASE_MANIFEST = CASES / "valid-minimal" / "package" / "manifest.json"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
UNIX = 3


class Entry(NamedTuple):
    name: str
    data: bytes
    symlink: bool = False


def manifest_with_files(files: dict) -> bytes:
    """Return the base manifest with one file evidence item per path in files."""
    manifest = json.loads(BASE_MANIFEST.read_text(encoding="utf-8"))
    for i, (path, data) in enumerate(files.items(), start=1):
        manifest["evidence"].append({
            "id": f"file-{i}",
            "kind": "other",
            "title": f"Example evidence file {i}",
            "issuer": {"name": "Example Supplier AG"},
            "scope": "Example Supplier AG.",
            "content": {
                "mode": "file",
                "path": path,
                "mediaType": "application/json" if path.endswith(".json") else "text/plain",
                "sha256": hashlib.sha256(data).hexdigest(),
            },
        })
    return (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


DATA = b"Example evidence file.\n"
JSON_DATA = b'{\n  "example": true\n}\n'
MINIMAL = BASE_MANIFEST.read_bytes()
WITH_FILE = manifest_with_files({"evidence/data.txt": DATA})
WITH_TWO_FILES = manifest_with_files({"evidence/data.txt": DATA, "evidence/data-2.txt": DATA})

ARCHIVES = {
    # Valid: manifest, an evidence/ directory entry, and one declared file.
    "valid-zip-package": [
        Entry("manifest.json", WITH_FILE),
        Entry("evidence/", b""),
        Entry("evidence/data.txt", DATA),
    ],
    # TEEF-PKG-04: the manifest is not at the archive root.
    "pkg-04-manifest-not-at-root": [
        Entry("package/manifest.json", MINIMAL),
    ],
    # TEEF-ARC-01: a file the manifest does not declare.
    "arc-01-undeclared-file": [
        Entry("manifest.json", MINIMAL),
        Entry("evidence/extra.txt", DATA),
    ],
    # TEEF-ARC-02: an entry escapes the archive through path traversal.
    "arc-02-path-traversal": [
        Entry("manifest.json", MINIMAL),
        Entry("evidence/../../escape.txt", DATA),
    ],
    # TEEF-ARC-02: an entry uses an absolute path.
    "arc-02-absolute-path": [
        Entry("manifest.json", MINIMAL),
        Entry("/etc/escape.txt", DATA),
    ],
    # TEEF-ARC-03: a declared file uses a reserved device name.
    "arc-03-reserved-name": [
        Entry("manifest.json", manifest_with_files({"evidence/con.json": JSON_DATA})),
        Entry("evidence/con.json", JSON_DATA),
    ],
    # TEEF-ARC-04: an entry is a symbolic link.
    "arc-04-symlink": [
        Entry("manifest.json", MINIMAL),
        Entry("evidence/link", b"../manifest.json", symlink=True),
    ],
    # TEEF-ARC-05: the manifest entry appears twice.
    "arc-05-duplicate-entry": [
        Entry("manifest.json", MINIMAL),
        Entry("manifest.json", MINIMAL),
    ],
    # TEEF-ARC-06: two entries differ only in case.
    "arc-06-case-collision": [
        Entry("manifest.json", manifest_with_files({"evidence/a.json": JSON_DATA})),
        Entry("evidence/a.json", JSON_DATA),
        Entry("evidence/A.json", JSON_DATA),
    ],
    # TEEF-ARC-07: more entries than context.limits.maxEntries allows,
    # even when the manifest entry is not counted.
    "arc-07-entry-limit": [
        Entry("manifest.json", WITH_TWO_FILES),
        Entry("evidence/data.txt", DATA),
        Entry("evidence/data-2.txt", DATA),
    ],
    # TEEF-ARC-07: more expanded bytes than context.limits.maxExpandedBytes allows.
    "arc-07-expanded-size-limit": [
        Entry("manifest.json", WITH_FILE),
        Entry("evidence/data.txt", DATA),
    ],
    # TEEF-ARC-07: a larger archive than context.limits.maxArchiveBytes allows.
    "arc-07-archive-size-limit": [
        Entry("manifest.json", WITH_FILE),
        Entry("evidence/data.txt", DATA),
    ],
}


def build(case: str, entries: list) -> bytes:
    """Return the ZIP bytes for one case."""
    buffer = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # duplicate names are intended
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as z:
            for entry in entries:
                info = zipfile.ZipInfo(entry.name, date_time=FIXED_TIME)
                info.create_system = UNIX
                info.compress_type = zipfile.ZIP_STORED
                if entry.symlink:
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                elif entry.name.endswith("/"):
                    info.external_attr = ((stat.S_IFDIR | 0o755) << 16) | 0x10
                else:
                    info.external_attr = (stat.S_IFREG | 0o644) << 16
                z.writestr(info, entry.data)
    return buffer.getvalue()


def main() -> None:
    for case, entries in ARCHIVES.items():
        target = CASES / case / "package.zip"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(build(case, entries))
        print(f"wrote {target.relative_to(CASES.parent.parent)}")


if __name__ == "__main__":
    main()
