import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import file_organizer


class CategoryMatchesTests(unittest.TestCase):
    def test_matches_category_extensions_case_insensitively(self):
        self.assertTrue(file_organizer.category_matches("report.DOCX", "1"))
        self.assertTrue(file_organizer.category_matches("photo.JpG", "2"))
        self.assertTrue(file_organizer.category_matches("movie.MP4", "3"))
        self.assertTrue(file_organizer.category_matches("notes.txt", "4"))
        self.assertTrue(file_organizer.category_matches("README", "4"))
        self.assertFalse(file_organizer.category_matches("photo.jpg", "4"))
        self.assertFalse(file_organizer.category_matches("notes.txt", "1"))


class OrganizeFilesTests(unittest.TestCase):
    def test_moves_matching_files_preserves_other_files_and_skips_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = source / "Rearranged"
            nested = source / "nested"
            nested.mkdir(parents=True)
            destination.mkdir()
            document = nested / "report.docx"
            other = source / "notes.txt"
            existing = destination / "report.docx"
            destination_file = destination / "already.docx"
            document.write_bytes(b"document")
            other.write_bytes(b"notes")
            existing.write_bytes(b"older document")
            destination_file.write_bytes(b"already sorted")

            with patch.object(Path, "open", side_effect=AssertionError("read file")):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    result = file_organizer.organize_files(source, destination, "1")

            self.assertEqual(result, (1, 1, 0))
            self.assertFalse(document.exists())
            self.assertTrue(other.exists())
            self.assertEqual((destination / "report (2).docx").read_bytes(), b"document")
            self.assertTrue(destination_file.exists())
            self.assertIn("Preserved (category mismatch)", output.getvalue())
            self.assertIn("T", output.getvalue())

    def test_a_failed_move_does_not_stop_processing_other_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            first = source / "first.jpg"
            second = source / "second.jpg"
            first.touch()
            second.touch()
            real_rename = file_organizer.os.rename

            def rename_with_failure(source_path, target_path):
                if Path(source_path).name == "first.jpg":
                    raise PermissionError("file is in use")
                real_rename(source_path, target_path)

            with patch.object(file_organizer.os, "rename", side_effect=rename_with_failure):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = file_organizer.organize_files(
                        source, root / "destination", "2"
                    )

            self.assertEqual(result, (1, 0, 1))
            self.assertTrue(first.exists())
            self.assertTrue((root / "destination" / "second.jpg").exists())

    def test_rejects_source_as_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            with self.assertRaisesRegex(ValueError, "must not be the source"):
                file_organizer.organize_files(source, source, "1")


if __name__ == "__main__":
    unittest.main()
