from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

SOURCE_FOLDER = Path("F:\\")
DESTINATION_FOLDER = SOURCE_FOLDER / "Rearranged"

CATEGORY_EXTENSIONS = {
    "1": {
        ".doc",
        ".docm",
        ".docx",
        ".dot",
        ".dotm",
        ".dotx",
        ".xls",
        ".xlsb",
        ".xlsm",
        ".xlsx",
        ".xlt",
        ".xltm",
        ".xltx",
        ".csv",
        ".tsv",
    },
    "2": {
        ".arw",
        ".bmp",
        ".cr2",
        ".dng",
        ".gif",
        ".heic",
        ".heif",
        ".jpeg",
        ".jpg",
        ".nef",
        ".png",
        ".raw",
        ".tif",
        ".tiff",
        ".webp",
    },
    "3": {
        ".3gp",
        ".aac",
        ".aiff",
        ".avi",
        ".flac",
        ".m4a",
        ".m4v",
        ".mkv",
        ".mov",
        ".mp3",
        ".mp4",
        ".mpeg",
        ".mpg",
        ".ogg",
        ".wav",
        ".webm",
        ".wma",
        ".wmv",
    },
}

CATEGORY_NAMES = {
    "1": "Word & Excel",
    "2": "Images",
    "3": "Audio & Video",
    "4": "All Other Files",
}


def category_matches(filename: str, category: str) -> bool:
    extension = Path(filename).suffix.lower()
    if category == "4":
        return not any(
            extension in extensions for extensions in CATEGORY_EXTENSIONS.values()
        )
    if category not in CATEGORY_EXTENSIONS:
        raise ValueError(f"Unknown category: {category}")
    return extension in CATEGORY_EXTENSIONS[category]


def unique_target(destination: Path, filename: str) -> Path:
    candidate = destination / filename
    if not candidate.exists():
        return candidate

    stem, suffix = Path(filename).stem, Path(filename).suffix
    index = 2
    while True:
        candidate = destination / f"{stem} ({index}){suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def log_action(action: str, path: Path, detail: str = "") -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    message = f"[{timestamp}] {action}: {path}"
    if detail:
        message += f" ({detail})"
    print(message, flush=True)


def organize_files(
    source: Path, destination: Path, category: str
) -> tuple[int, int, int]:
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if not source.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {source}")
    if destination == source:
        raise ValueError("Destination must not be the source folder.")
    if category not in CATEGORY_NAMES:
        raise ValueError(f"Unknown category: {category}")

    destination.mkdir(parents=True, exist_ok=True)
    destination_key = os.path.normcase(os.path.abspath(destination))
    moved = skipped = failed = 0

    def report_scan_error(error: OSError) -> None:
        nonlocal failed
        failed += 1
        log_action("Could not scan", Path(error.filename or source), str(error))

    log_action("Started scan", source, f"category: {CATEGORY_NAMES[category]}")
    for current_root, directories, filenames in os.walk(
        source, onerror=report_scan_error
    ):
        directories.sort(key=str.casefold)
        filenames.sort(key=str.casefold)
        current_path = Path(current_root)
        directories[:] = [
            directory
            for directory in directories
            if os.path.normcase(os.path.abspath(current_path / directory))
            != destination_key
        ]

        for filename in filenames:
            file_path = current_path / filename
            if not category_matches(filename, category):
                skipped += 1
                log_action("Preserved (category mismatch)", file_path)
                continue

            try:
                target = unique_target(destination, filename)
                while True:
                    try:
                        os.rename(file_path, target)
                        break
                    except FileExistsError:
                        if not target.exists():
                            raise
                        target = unique_target(destination, filename)
                moved += 1
                log_action("Moved", file_path, f"to {target}")
            except OSError as error:
                failed += 1
                log_action("Could not move", file_path, str(error))

    log_action(
        "Finished",
        source,
        f"moved {moved}, preserved {skipped}, failed {failed}",
    )
    return moved, skipped, failed


def main() -> None:
    print("Choose a file category to move from F:\\ to F:\\Rearranged:")
    for number, name in CATEGORY_NAMES.items():
        print(f"  {number}. {name}")

    while True:
        try:
            category = input("Enter 1, 2, 3, or 4: ").strip()
        except EOFError:
            print("No category was selected.")
            return
        if category in CATEGORY_NAMES:
            break
        print("Please enter 1, 2, 3, or 4.")

    try:
        organize_files(SOURCE_FOLDER, DESTINATION_FOLDER, category)
    except (OSError, ValueError) as error:
        log_action("Organizer stopped", SOURCE_FOLDER, str(error))
        raise SystemExit(1) from error

    input("Press Enter to close.")


if __name__ == "__main__":
    main()
