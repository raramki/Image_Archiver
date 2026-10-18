$ErrorActionPreference = "Stop"

$target = Join-Path $PSScriptRoot "File_Organizer.exe"
if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
    throw "File_Organizer.exe was not found. Run Build_File_Organizer.bat first."
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "File Organizer.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.Description = "Organize files from F:\ into F:\Rearranged"
$shortcut.Save()

Write-Host "Created desktop shortcut: $shortcutPath"
