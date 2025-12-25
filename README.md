# NTFS Filename Sanitizer

A Python script to automatically sanitize filenames and directory names to be compatible with NTFS file systems (Windows). This tool is particularly useful when transferring files from Linux/Unix systems to Windows-formatted drives.

## Table of Contents

- [Overview](#overview)
- [The Linux to NTFS Problem](#the-linux-to-ntfs-problem)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [What Gets Sanitized](#what-gets-sanitized)
- [Examples](#examples)
- [Safety Features](#safety-features)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## Overview

This Python script recursively processes directories and renames files/folders to comply with NTFS filesystem restrictions. It handles forbidden characters, reserved names, trailing spaces/dots, and excessive filename lengths that can cause issues on Windows systems.

## The Linux to NTFS Problem

### Why This Tool Exists

When working with files on Linux, you may encounter filenames that are perfectly valid on ext4, btrfs, or other Linux filesystems but cause problems when copied to NTFS-formatted drives (commonly used on Windows and external drives). 

**Common scenarios:**

- Files downloaded or created on Linux with characters like `:`, `?`, `*`, `|`, `<`, `>` in their names
- Filenames ending with spaces or dots (which Windows silently strips, causing confusion)
- Files named after Windows reserved names like `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`
- Very long filenames that exceed NTFS's 255-character limit

### What Happens Without Sanitization

When you try to copy these files to an NTFS drive, you may experience:

- **Copy failures** with cryptic error messages
- **Silent truncation** of trailing spaces/dots, potentially causing file collisions
- **Complete inability to access** files with reserved names
- **Data loss risk** if the filesystem can't handle the filenames properly

This script solves these issues by preprocessing your files before transfer, ensuring smooth compatibility between Linux and NTFS systems.

## Features

- **Automatic detection and replacement** of NTFS-forbidden characters (`< > : " / \ | ? *` and control characters)
- **Handles reserved Windows filenames** (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
- **Removes trailing spaces and dots** that Windows strips automatically
- **Enforces maximum filename length** (default 255 characters, configurable)
- **Collision detection** with automatic numbering for duplicate names
- **Dry-run mode** to preview changes before applying them
- **Recursive processing** of entire directory trees
- **Detailed logging** of all changes made
- **Safe operation** that processes children before parents to avoid path issues

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library modules)

## Installation

1. Download the script from GitHub:
```bash
git clone https://github.com/cypher-me/ntfs-sanitizer.git
cd ntfs-sanitizer
```

Or download just the script file:
```bash
wget https://raw.githubusercontent.com/cypher-me/ntfs-sanitizer/main/ntfs_sanitizer.py
# or
curl -O https://raw.githubusercontent.com/cypher-me/ntfs-sanitizer/main/ntfs_sanitizer.py
```

2. Place the script in the same directory where you need to sanitize files:
```bash
# Copy the script to your target directory
cp ntfs_sanitizer.py /path/to/your/files/
cd /path/to/your/files/
```

3. Make it executable (Linux/Mac):
```bash
chmod +x ntfs_sanitizer.py
```

**Note:** The script should be run from within or pointed at the directory containing the files you want to sanitize. No additional Python packages need to be installed - the script uses only standard library modules.

## Usage

### Basic Syntax

```bash
python ntfs_sanitizer.py [directory] [options]
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `directory` | Path to directory to process | Current directory |
| `--dry-run` | Preview changes without applying them | False |
| `--max-length` | Maximum filename length | 255 |
| `-h, --help` | Show help message | - |

### Common Usage Patterns

```bash
# Process current directory (dry run to preview)
python ntfs_sanitizer.py --dry-run

# Process current directory (apply changes)
python ntfs_sanitizer.py

# Process specific directory
python ntfs_sanitizer.py /path/to/downloads

# Process with custom max length
python ntfs_sanitizer.py --max-length 100 ~/Documents

# Preview changes for specific directory
python ntfs_sanitizer.py ~/Downloads --dry-run
```

## What Gets Sanitized

### 1. Forbidden Characters

The following characters are replaced with underscores (`_`):

- `<` (less than)
- `>` (greater than)
- `:` (colon)
- `"` (double quote)
- `/` (forward slash)
- `\` (backslash)
- `|` (pipe)
- `?` (question mark)
- `*` (asterisk)
- Control characters (ASCII 0-31)

**Example:**
```
file<name>:test?.txt  →  file_name__test_.txt
```

### 2. Trailing Spaces and Dots

Windows automatically strips trailing spaces and dots, which can cause file collisions. These are removed.

**Example:**
```
"document.txt "  →  "document.txt"
"folder..."      →  "folder"
```

### 3. Reserved Windows Names

Files matching reserved names get prefixed with an underscore:

- CON, PRN, AUX, NUL
- COM1 through COM9
- LPT1 through LPT9

**Example:**
```
CON.txt     →  _CON.txt
aux.config  →  _aux.config
```

### 4. Excessive Length

Filenames longer than the specified maximum (default 255) are truncated while preserving file extensions.

**Example:**
```
very_long_filename_that_exceeds_the_maximum_allowed_length[...].txt
  →  very_long_filename_that_exceeds_the_maximum_al.txt
```

### 5. Collision Handling

If a sanitized name already exists, a counter is appended:

**Example:**
```
file?.txt  →  file_.txt
If file_.txt exists:  →  file__1.txt
If file__1.txt exists:  →  file__2.txt
```

## Examples

### Example 1: Dry Run Preview

```bash
$ python ntfs_sanitizer.py ~/Downloads --dry-run

--- Starting NTFS Sanitization ---
Directory: /home/user/Downloads
Dry run: True
--------------------------------------------------
[WOULD CHANGE]
  Location: ./
  Original: video:720p.mp4
  Modified: video_720p.mp4
  Reason: Contains invalid NTFS characters
------------------------------
[WOULD CHANGE]
  Location: ./documents
  Original: CON.txt
  Modified: _CON.txt
  Reason: Reserved Windows name
------------------------------

--- Process Complete ---
Total renamed: 2
Skipped (too long): 0
Errors: 0

Note: This was a dry run. No files were actually changed.
Run without --dry-run to apply changes.
```

### Example 2: Actual Rename Operation

```bash
$ python ntfs_sanitizer.py ~/Downloads

--- Starting NTFS Sanitization ---
Directory: /home/user/Downloads
Dry run: False
--------------------------------------------------
[CHANGED]
  Location: ./
  Original: video:720p.mp4
  Modified: video_720p.mp4
  Reason: Contains invalid NTFS characters
------------------------------

--- Process Complete ---
Total renamed: 1
Skipped (too long): 0
Errors: 0
```

## Safety Features

1. **Dry Run Mode**: Always test with `--dry-run` first to preview changes
2. **Collision Detection**: Automatically handles duplicate names with counters
3. **Preserves Extensions**: File extensions are maintained during truncation
4. **Bottom-Up Processing**: Renames children before parents to avoid path issues
5. **Error Handling**: Continues processing even if individual renames fail
6. **Detailed Logging**: Shows exactly what changed and why

## Limitations

- Does not modify file contents, only names
- Cannot process files the user lacks permission to rename
- Does not handle symlinks specially (processes them as regular files/directories)
- Maximum path length limitations may still apply on some systems (260 characters on older Windows)
- Does not validate whether names are problematic for specific software applications

## Best Practices

1. **Always run with `--dry-run` first** to preview changes
2. **Backup important data** before running the script
3. **Close applications** that might have files open in the target directory
4. **Run from parent directory** rather than within the directory being processed
5. **Check results** after running to ensure expected outcome

## Troubleshooting

### "Permission denied" errors
- Ensure you have write permissions for the directory
- Close any applications using files in the directory
- On Linux, you may need to run with `sudo` for system directories (not recommended)

### Files still won't copy to NTFS
- Check total path length (Windows has 260-character path limit on older systems)
- Verify the NTFS drive is properly mounted with write permissions
- Some characters may be problematic for specific software even if NTFS-compliant

### Changes not taking effect
- Ensure you're not running with `--dry-run` flag
- Check that the script completed without errors
- Verify you're checking the correct directory

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests for:

- Bug fixes
- Additional sanitization rules
- Performance improvements
- Better error handling
- Documentation improvements

## License

This project is released into the public domain. Use it freely for any purpose.

---

**Disclaimer**: Always backup your data before running batch rename operations. While this script includes safety features, the authors are not responsible for any data loss.
