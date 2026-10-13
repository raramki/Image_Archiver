import contextlib
import io
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import image_archiver


class ParseYearRangeTests(unittest.TestCase):
    def test_single_year_and_inclusive_range(self):
        self.assertEqual(image_archiver.parse_year_range("2021"), (2021, 2021))
        self.assertEqual(image_archiver.parse_year_range(" 2020-2022 "), (2020, 2022))

    def test_invalid_ranges(self):
        for value in ("", "2022-2020", "0", "9999", "2020-2021-2022", "year"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                image_archiver.parse_year_range(value)


class CopyImagesTests(unittest.TestCase):
    def test_copies_by_mocked_creation_time_and_skips_duplicate_contents(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "archive"
            nested = source / "nested"
            nested.mkdir(parents=True)
            first = source / "first.JPG"
            duplicate = nested / "same.jpg"
            out_of_range = source / "old.png"
            unsupported = source / "notes.txt"
            first.write_bytes(b"same image")
            duplicate.write_bytes(b"same image")
            out_of_range.write_bytes(b"old image")
            unsupported.write_bytes(b"not an image")

            with patch.object(
                image_archiver,
                "creation_timestamp",
                side_effect=[
                    datetime(2021, 4, 3).timestamp(),
                    datetime(2019, 1, 1).timestamp(),
                    datetime(2021, 4, 4).timestamp(),
                ],
            ), contextlib.redirect_stdout(io.StringIO()):
                result = image_archiver.copy_images(source, destination, 2020, 2022)

            self.assertEqual(result, (1, 1, 0))
            self.assertEqual(
                sorted(path.name for path in (destination / "2021-04").iterdir()),
                ["first.JPG"],
            )
            self.assertFalse((destination / "2019-01").exists())

    def test_rejects_destination_inside_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            with self.assertRaisesRegex(ValueError, "inside it"):
                image_archiver.copy_images(source, source / "archive", 2020, 2020)

    def test_uses_suffix_when_filename_already_exists(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            (folder / "photo.png").touch()
            (folder / "photo (2).png").touch()
            self.assertEqual(
                image_archiver.unique_target(folder, "photo.png").name,
                "photo (3).png",
            )


if __name__ == "__main__":
    unittest.main()
