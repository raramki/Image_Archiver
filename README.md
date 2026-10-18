# Windows File Utilities

This project contains two independent Windows utilities: **File Organizer**
prompts for a drive and sorts files into that drive's `Rearranged` folder, and
**Image Archiver** copies images into monthly folders in `D:\Image Archive`.

## File Organizer

Double-click `Run_File_Organizer.bat`, or build the standalone
`File_Organizer.exe` and double-click it. Select one of the available Windows
drive letters, then choose one of the four categories:

1. Word & Excel (`.doc`, `.docx`, `.xls`, `.xlsx`, and related formats)
2. Images (common web and camera image formats)
3. Audio & Video (common audio and video formats)
4. All Other Files (extensions not included in the first three categories,
   including files without an extension)

The organizer scans the selected drive recursively, excludes its
`Rearranged` folder from the scan, and moves matching files into a category
subfolder: `WordExcel`, `Images`, `AudioVideo`, or `OtherFiles`. Nonmatching
files are left where they are. If a destination filename already exists, a
numeric suffix is added rather than overwriting it. Each file outcome and scan
summary is written to the console with a timestamp. A failure to move an
individual file is logged and does not stop the remaining work.

Classification uses only filenames and extensions. The organizer does not open
or read file contents; matching files are moved with a filesystem rename. Duplicate
detection is also metadata-only: a file is treated as a duplicate when its
case-insensitive filename, size, and last-modified timestamp match a file
already in that category folder or found earlier during the scan. The later
copy is deleted. This timestamp-based match does not verify file contents, so
different files with identical metadata can be treated as duplicates.

If Windows reports a cyclic redundancy check (CRC) or data error on the
selected drive, stop using it and back up any accessible data. This is a
drive/filesystem read error, not a file-category error. Check the drive with
`chkdsk <drive>:`; use repair options only after backing up important data.

### Build and install the desktop shortcut

Install Python 3.10 or newer and PyInstaller:

```bat
python -m pip install pyinstaller
```

Run `Build_File_Organizer.bat` to create the standalone
`File_Organizer.exe` and `File_Organizer_Windows.zip`. Extract the ZIP to a
permanent folder, then run `Create_Desktop_Shortcut.bat` from that folder. The
shortcut points to the executable in the extracted folder, so keep that folder
in place.

The organizer can also run from source with Python:

```bat
python file_organizer.py
```

## Image Archiver

The existing image archiver recursively finds image files by filesystem
creation year, skips duplicate file contents, and copies them into monthly
folders such as `D:\Image Archive\2021-04`.

On Windows, double-click `Run_Image_Archiver.bat`. The default source is
`F:\` and the default destination is `D:\Image Archive`. To choose different
folders, run:

```bat
Run_Image_Archiver.bat --source "E:\Pictures" --destination "D:\Image Archive"
```

When prompted, enter one year (for example `2021`) or an inclusive range (for
example `2020-2022`). The archiver copies images with a filesystem creation
year in that range. It uses the creation month for the `YYYY-MM` folder name,
preserves file metadata with `copy2`, and does not modify or delete source
files. Duplicate content is detected using SHA-256; matching images are
skipped. When different images have the same name in a month folder, a numeric
suffix is added.

Supported extensions: BMP, GIF, HEIC, HEIF, JPEG, JPG, PNG, TIF, TIFF, and
WEBP. The destination cannot be the source folder or a folder inside the source.
Creation-time metadata differs by operating system; Windows provides file
creation time as the timestamp used by this tool.

`Build_Image_Archiver.bat` builds the existing image archiver executable and
`Image_Archiver_Windows.zip`.

## Tests

Run the standard-library test suite with:

```bat
python -m unittest discover -s tests -v
```
