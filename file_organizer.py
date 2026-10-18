from __future__ import annotations

import ctypes
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, NamedTuple

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
    "5": "All Categories",
}

CATEGORY_FOLDERS = {
    "1": "WordExcel",
    "2": "Images",
    "3": "AudioVideo",
    "4": "OtherFiles",
}


class FileFingerprint(NamedTuple):
    filename: str
    size: int
    modified_ns: int


def available_drives() -> list[str]:
    if os.name != "nt":
        raise OSError("Drive selection is supported only on Windows.")

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    get_logical_drives = kernel32.GetLogicalDrives
    get_logical_drives.restype = ctypes.c_uint32
    drive_mask = get_logical_drives()
    if not drive_mask:
        raise ctypes.WinError(ctypes.get_last_error())
    return [
        chr(ord("A") + index)
        for index in range(26)
        if drive_mask & (1 << index)
    ]


def select_drive(input_func: Callable[[str], str] | None = None) -> str:
    drives = available_drives()
    if not drives:
        raise OSError("Windows did not report any available drives.")
    if input_func is None:
        input_func = input

    print("Available drives:")
    for drive in drives:
        print(f"  {drive}:\\")

    while True:
        try:
            selected = input_func("Enter a drive letter (for example, D): ").strip()
        except EOFError:
            raise
        letter = selected.rstrip("\\/:").upper()
        if len(letter) == 1 and letter in drives:
            return letter
        print(f"Please choose one of the listed drives: {', '.join(drives)}.")


def category_matches(filename: str, category: str) -> bool:
    extension = Path(filename).suffix.lower()
    if category == "4":
        return not any(
            extension in extensions for extensions in CATEGORY_EXTENSIONS.values()
        )
    if category not in CATEGORY_EXTENSIONS:
        raise ValueError(f"Unknown category: {category}")
    return extension in CATEGORY_EXTENSIONS[category]


def category_for_filename(filename: str) -> str:
    for category, extensions in CATEGORY_EXTENSIONS.items():
        if Path(filename).suffix.lower() in extensions:
            return category
    return "4"


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


def file_fingerprint(path: Path) -> FileFingerprint:
    metadata = path.stat()
    return FileFingerprint(
        path.name.casefold(),
        metadata.st_size,
        metadata.st_mtime_ns,
    )


def log_action(action: str, path: Path, detail: str = "") -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    message = f"[{timestamp}] {action}: {path}"
    if detail:
        message += f" ({detail})"
    print(message, flush=True)


def organize_files(
    source: Path, destination_root: Path, category: str
) -> tuple[int, int, int, int]:
    source = source.resolve(strict=True)
    destination_root = Path(os.path.abspath(destination_root))
    if not source.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {source}")
    if os.path.normcase(os.path.abspath(destination_root)) == os.path.normcase(
        os.path.abspath(source)
    ):
        raise ValueError("Destination must not be the source folder.")
    if category not in CATEGORY_NAMES:
        raise ValueError(f"Unknown category: {category}")

    categories = list(CATEGORY_EXTENSIONS) + ["4"] if category == "5" else [category]
    destinations = {
        current_category: destination_root / CATEGORY_FOLDERS[current_category]
        for current_category in categories
    }
    destination_root_key = os.path.normcase(os.path.abspath(destination_root))
    moved = skipped = duplicates = failed = 0
    seen_fingerprints: dict[str, set[FileFingerprint]] = {
        current_category: set() for current_category in categories
    }

    for current_category, destination in destinations.items():
        try:
            destination.mkdir(parents=True, exist_ok=True)
            with os.scandir(destination) as entries:
                for entry in entries:
                    if not entry.is_file(follow_symlinks=False):
                        continue
                    existing_path = Path(entry.path)
                    try:
                        seen_fingerprints[current_category].add(
                            file_fingerprint(existing_path)
                        )
                    except OSError as error:
                        failed += 1
                        log_action(
                            "Could not inspect metadata", existing_path, str(error)
                        )
        except OSError as error:
            failed += 1
            log_action("Could not scan destination", destination, str(error))
            return moved, skipped, duplicates, failed

    def report_scan_error(error: OSError) -> None:
        nonlocal failed
        failed += 1
        log_action("Could not scan", Path(error.filename or source), str(error))

    log_action(
        "Started scan",
        source,
        f"category: {CATEGORY_NAMES[category]}, destination root: {destination_root}",
    )
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
            != destination_root_key
        ]

        for filename in filenames:
            file_path = current_path / filename
            if category == "5":
                file_category = category_for_filename(filename)
            elif category_matches(filename, category):
                file_category = category
            else:
                skipped += 1
                log_action("Preserved (category mismatch)", file_path)
                continue

            try:
                destination = destinations[file_category]
                fingerprint = file_fingerprint(file_path)
                if fingerprint in seen_fingerprints[file_category]:
                    file_path.unlink()
                    duplicates += 1
                    log_action(
                        "Deleted duplicate",
                        file_path,
                        "same filename, size, and last-modified timestamp",
                    )
                    continue

                target = unique_target(destination, filename)
                while True:
                    try:
                        os.rename(file_path, target)
                        break
                    except FileExistsError:
                        if not target.exists():
                            raise
                        target = unique_target(destination, filename)
                seen_fingerprints[file_category].add(fingerprint)
                moved += 1
                log_action("Moved", file_path, f"to {target}")
            except OSError as error:
                failed += 1
                log_action("Could not move", file_path, str(error))

    log_action(
        "Finished",
        source,
        f"moved {moved}, deleted duplicates {duplicates}, "
        f"preserved {skipped}, failed {failed}",
    )
    return moved, skipped, duplicates, failed


def main() -> None:
    try:
        drive = select_drive()
    except EOFError:
        print("No drive was selected.")
        return
    except OSError as error:
        log_action("Could not list drives", Path("."), str(error))
        raise SystemExit(1) from error

    source = Path(f"{drive}:\\")
    destination = source / "Rearranged"
    print(f"Choose a file category to move from {source} to {destination}:")
    for number, name in CATEGORY_NAMES.items():
        if number == "5":
            print(f"  {number}. {name} -> all category folders")
        else:
            print(f"  {number}. {name} -> {CATEGORY_FOLDERS[number]}")

    while True:
        try:
            category = input("Enter 1, 2, 3, 4, or 5: ").strip()
        except EOFError:
            print("No category was selected.")
            return
        if category in CATEGORY_NAMES:
            break
        print("Please enter 1, 2, 3, 4, or 5.")

    try:
        organize_files(source, destination, category)
    except (OSError, ValueError) as error:
        error_path = Path(error.filename) if error.filename else source
        log_action("Organizer stopped", error_path, str(error))
        raise SystemExit(1) from error

    input("Press Enter to close.")


if __name__ == "__main__":
    main()
