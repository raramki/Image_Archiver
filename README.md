# Image Archiver

A standard-library Python tool that recursively finds image files by filesystem
creation year, skips duplicate file contents, and copies them into monthly
folders such as `D:\Image Archive\2021-04`.

## Run

On Windows, double-click `Run_Image_Archiver.bat`. It runs the included
`Image_Archiver.exe` when available, or runs the Python source if Python 3.10+
is installed. The default source is `F:\` and the default destination is
`D:\Image Archive`.

To choose different folders, run:

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
WEBP. The program reports copied files, duplicates, and failures. It does not
create a folder-summary CSV.

The destination cannot be the source folder or a folder inside the source.
Creation-time metadata differs by operating system; Windows provides file
creation time as the timestamp used by this tool.

## Build the standalone executable and ZIP

Install Python 3.10 or newer and PyInstaller:

```bat
python -m pip install pyinstaller
```

Then double-click `Build_Image_Archiver.bat` or run it from Command Prompt. It
builds a one-file console executable and creates `Image_Archiver_Windows.zip`
containing the executable, source, launcher, build script, and this README.

## Test

Run the standard-library test suite with:

```bat
python -m unittest discover -s tests -v
```
