from __future__ import annotations

import argparse
import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path

IMAGE_EXTENSIONS = {
    ".bmp",
    ".gif",
    ".heic",
    ".heif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


def creation_timestamp(stat: os.stat_result) -> float:
    """Return the platform's file-creation timestamp."""
    return getattr(stat, "st_birthtime", stat.st_ctime)


def parse_year_range(value: str) -> tuple[int, int]:
    parts = value.strip().split("-")
    if len(parts) == 1:
        parts *= 2
    if len(parts) != 2:
        raise ValueError("Enter one year or a year range such as 2020-2022.")
    try:
        start_year, end_year = (int(part.strip()) for part in parts)
    except ValueError as error:
        raise ValueError("Years must be numbers, for example 2020-2022.") from error
    if not (1 <= start_year <= end_year <= 9998):
        raise ValueError("Enter a valid range with start year no later than end year.")
    return start_year, end_year


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as image_file:
        for block in iter(lambda: image_file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def unique_target(month_folder: Path, filename: str) -> Path:
    candidate = month_folder / filename
    if not candidate.exists():
        return candidate
    stem, suffix = Path(filename).stem, Path(filename).suffix
    index = 2
    while True:
        candidate = month_folder / f"{stem} ({index}){suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def copy_images(
    source: Path, destination: Path, start_year: int, end_year: int
) -> tuple[int, int, int]:
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if not source.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {source}")
    if destination == source or source in destination.parents:
        raise ValueError("Destination must not be the source folder or inside it.")
    destination.mkdir(parents=True, exist_ok=True)

    seen_hashes: set[str] = set()
    destination_hashes_by_month: dict[str, dict[str, Path]] = {}
    copied = duplicates = failed = 0

    def report_scan_error(error: OSError) -> None:
        nonlocal failed
        failed += 1
        print(f"Could not scan {error.filename}: {error}")

    for current_root, directories, filenames in os.walk(
        source, onerror=report_scan_error
    ):
        directories.sort(key=str.casefold)
        filenames.sort(key=str.casefold)
        for filename in filenames:
            if Path(filename).suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            image_path = Path(current_root) / filename
            try:
                stat = image_path.stat()
                created_at = datetime.fromtimestamp(creation_timestamp(stat))
                if not start_year <= created_at.year <= end_year:
                    continue
                month = created_at.strftime("%Y-%m")
                image_hash = sha256_file(image_path)
            except (OSError, OverflowError, ValueError) as error:
                failed += 1
                print(f"Could not inspect {image_path}: {error}")
                continue

            if image_hash in seen_hashes:
                duplicates += 1
                continue

            if month not in destination_hashes_by_month:
                month_folder = destination / month
                hashes: dict[str, Path] = {}
                if month_folder.is_dir():
                    try:
                        archived_files = sorted(
                            month_folder.iterdir(),
                            key=lambda path: path.name.casefold(),
                        )
                    except OSError as error:
                        failed += 1
                        print(f"Could not scan {month_folder}: {error}")
                        archived_files = []
                    for archived in archived_files:
                        if (
                            archived.is_file()
                            and archived.suffix.lower() in IMAGE_EXTENSIONS
                        ):
                            try:
                                hashes.setdefault(sha256_file(archived), archived)
                            except OSError as error:
                                failed += 1
                                print(f"Could not inspect {archived}: {error}")
                destination_hashes_by_month[month] = hashes

            if image_hash in destination_hashes_by_month[month]:
                duplicates += 1
                seen_hashes.add(image_hash)
                continue

            try:
                month_folder = destination / month
                month_folder.mkdir(parents=True, exist_ok=True)
                target = unique_target(month_folder, filename)
                shutil.copy2(image_path, target)
                destination_hashes_by_month[month][image_hash] = target
                seen_hashes.add(image_hash)
                copied += 1
            except OSError as error:
                failed += 1
                print(f"Could not copy {image_path}: {error}")

    print(
        f"\nFinished: copied {copied} image(s), "
        f"skipped {duplicates} duplicate(s), {failed} failure(s)."
    )
    print(f"Destination: {destination}")
    return copied, duplicates, failed


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Copy unique images created within a selected year range "
            "into YYYY-MM folders."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("F:\\"),
        help="Source drive or folder (default: F:\\)",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path(r"D:\Image Archive"),
        help=r"Destination folder (default: D:\Image Archive)",
    )
    args = parser.parse_args()

    while True:
        try:
            value = input(
                "Enter creation year or inclusive range (e.g. 2020-2022): "
            ).strip()
        except EOFError:
            parser.error("No year or year range was provided.")
        try:
            start, end = parse_year_range(value)
            break
        except ValueError as error:
            print(error)

    try:
        copy_images(args.source, args.destination, start, end)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
