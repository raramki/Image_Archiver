# Windows File Utilities

This project contains two independent Windows utilities: **File Organizer**
sorts files from `F:\` into `F:\Rearranged`, and **Image Archiver** copies
images into monthly folders in `D:\Image Archive`.

## File Organizer

Double-click `Run_File_Organizer.bat`, or build the standalone
`File_Organizer.exe` and double-click it. Choose one of the four categories:

1. Word & Excel (`.doc`, `.docx`, `.xls`, `.xlsx`, and related formats)
2. Images (common web and camera image formats)
3. Audio & Video (common audio and video formats)
4. All Other Files (extensions not included in the first three categories,
   including files without an extension)

The organizer scans `F:\` recursively, excludes `F:\Rearranged` from the scan,
and moves matching files into `F:\Rearranged`. Nonmatching files are left
where they are. If a destination filename already exists, a numeric suffix is
added rather than overwriting it. Each file outcome and scan summary is written
to the console with a timestamp. A failure to move an individual file is logged
and does not stop the remaining work.

Classification uses only filenames and extensions. The organizer does not open
or read file contents; matching files are moved with a filesystem rename. The
source and destination are fixed to the F: drive.

If Windows reports a cyclic redundancy check (CRC) or data error on
`F:\Rearranged`, stop using the drive and back up any accessible data. This is a
drive/filesystem read error, not a file-category error. Check the drive with
`chkdsk F:`; use repair options only after backing up important data.

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
