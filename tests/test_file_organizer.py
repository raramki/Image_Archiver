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
        self.assertEqual(
            file_organizer.CATEGORY_FOLDERS,
            {"1": "WordExcel", "2": "Images", "3": "AudioVideo", "4": "OtherFiles"},
        )


class DriveSelectionTests(unittest.TestCase):
    def test_lists_drives_and_accepts_letter_with_colon(self):
        with patch.object(file_organizer, "available_drives", return_value=["C", "F"]):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                selected = file_organizer.select_drive(lambda _prompt: "f:")

        self.assertEqual(selected, "F")
        self.assertIn("C:\\", output.getvalue())
        self.assertIn("F:\\", output.getvalue())

    def test_reprompts_when_drive_is_not_available(self):
        answers = iter(["Z", "C"])
        with patch.object(file_organizer, "available_drives", return_value=["C", "D"]):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                selected = file_organizer.select_drive(lambda _prompt: next(answers))

        self.assertEqual(selected, "C")
        self.assertIn("Please choose one of the listed drives", output.getvalue())

    def test_reports_empty_drive_list(self):
        with patch.object(file_organizer, "available_drives", return_value=[]):
            with self.assertRaisesRegex(OSError, "any available drives"):
                file_organizer.select_drive(lambda _prompt: "C")


class OrganizeFilesTests(unittest.TestCase):
    def test_does_not_resolve_destination_path_before_using_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "destination"
            source.mkdir()
            original_resolve = Path.resolve

            def resolve_source_only(path, *args, **kwargs):
                if path == destination:
                    raise AssertionError("destination should not be resolved")
                return original_resolve(path, *args, **kwargs)

            with patch.object(Path, "resolve", resolve_source_only):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = file_organizer.organize_files(source, destination, "1")

            self.assertEqual(result, (0, 0, 0))
            self.assertTrue(destination.is_dir())

    def test_moves_matching_files_preserves_other_files_and_skips_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = source / "Rearranged"
            nested = source / "nested"
            nested.mkdir(parents=True)
            word_excel_destination = destination / "WordExcel"
            images_destination = destination / "Images"
            word_excel_destination.mkdir(parents=True)
            images_destination.mkdir()
            document = nested / "report.docx"
            other = source / "notes.txt"
            existing = word_excel_destination / "report.docx"
            destination_file = images_destination / "already.docx"
            other_category_file = images_destination / "existing.jpg"
            document.write_bytes(b"document")
            other.write_bytes(b"notes")
            existing.write_bytes(b"older document")
            destination_file.write_bytes(b"already sorted")
            other_category_file.write_bytes(b"already categorized")

            with patch.object(Path, "open", side_effect=AssertionError("read file")):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    result = file_organizer.organize_files(source, destination, "1")

            self.assertEqual(result, (1, 1, 0))
            self.assertFalse(document.exists())
            self.assertTrue(other.exists())
            self.assertEqual(
                (word_excel_destination / "report (2).docx").read_bytes(), b"document"
            )
            self.assertTrue(destination_file.exists())
            self.assertTrue(other_category_file.exists())
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
            self.assertTrue(
                (root / "destination" / "Images" / "second.jpg").exists()
            )

    def test_rejects_source_as_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            with self.assertRaisesRegex(ValueError, "must not be the source"):
                file_organizer.organize_files(source, source, "1")


if __name__ == "__main__":
    unittest.main()
