"""Tests for build_archives.py. Run: python conformance/tools/test_build_archives.py"""
import io
import pathlib
import stat
import sys
import unittest
import zipfile

TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from build_archives import ARCHIVES, build  # noqa: E402

CASES = TOOLS.parent / "0.1.0"


def case_named(suffix):
    return next(k for k in ARCHIVES if k.endswith(suffix))


class BuildArchivesTest(unittest.TestCase):
    def test_build_is_deterministic(self):
        for case, entries in ARCHIVES.items():
            self.assertEqual(build(case, entries), build(case, entries), case)

    def test_timestamps_are_fixed(self):
        for case, entries in ARCHIVES.items():
            with zipfile.ZipFile(io.BytesIO(build(case, entries))) as z:
                for info in z.infolist():
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0), case)

    def test_symlink_entry_has_link_mode(self):
        case = case_named("-symlink")
        with zipfile.ZipFile(io.BytesIO(build(case, ARCHIVES[case]))) as z:
            link = next(i for i in z.infolist() if i.filename == "evidence/link")
            self.assertEqual(stat.S_IFMT(link.external_attr >> 16), stat.S_IFLNK)

    def test_duplicate_entry_is_kept(self):
        case = case_named("-duplicate-entry")
        with zipfile.ZipFile(io.BytesIO(build(case, ARCHIVES[case]))) as z:
            self.assertEqual([i.filename for i in z.infolist()].count("manifest.json"), 2)

    def test_every_archive_case_has_case_json(self):
        for case in ARCHIVES:
            self.assertTrue((CASES / case / "case.json").is_file(), case)


if __name__ == "__main__":
    unittest.main()
