"""Platform detection and path sanitization utilities."""

import os
import re
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def is_macos() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"


def is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform.startswith("linux")


# Windows reserved characters: < > : " / \ | ? *
# Also problematic: & (in cmd.exe), ^ (escape char), % (env vars)
WINDOWS_INVALID_CHARS = re.compile(r'[<>:"/\\|?*&^%]')

# Windows reserved filenames (case-insensitive)
WINDOWS_RESERVED_NAMES = frozenset([
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
])

# Maximum filename length (not full path) on most filesystems
MAX_FILENAME_LENGTH = 255

# Windows MAX_PATH is 260, but we leave room for the base path
WINDOWS_SAFE_FILENAME_LENGTH = 200


def sanitize_filename(filename: str, for_windows: bool | None = None) -> str:
    """
    Sanitize a filename for the target platform.

    Args:
        filename: The filename to sanitize
        for_windows: If True, apply Windows restrictions. If False, skip them.
                    If None (default), auto-detect based on current platform.

    Returns:
        Sanitized filename safe for the target platform
    """
    if for_windows is None:
        for_windows = is_windows()

    if not for_windows:
        return filename

    # Split extension from base name
    if "." in filename:
        base, ext = filename.rsplit(".", 1)
        ext = "." + ext
    else:
        base = filename
        ext = ""

    # Replace invalid characters with underscore
    base = WINDOWS_INVALID_CHARS.sub("_", base)

    # Remove leading/trailing spaces and dots (Windows doesn't allow trailing dots)
    base = base.strip(" .")

    # Check for reserved names (without extension)
    if base.upper() in WINDOWS_RESERVED_NAMES:
        base = base + "_file"

    # Truncate if too long
    max_base_len = WINDOWS_SAFE_FILENAME_LENGTH - len(ext)
    if len(base) > max_base_len:
        base = base[:max_base_len]

    return base + ext


def sanitize_directory_name(dirname: str, for_windows: bool | None = None) -> str:
    """
    Sanitize a directory name for the target platform.

    Args:
        dirname: The directory name to sanitize
        for_windows: If True, apply Windows restrictions. If False, skip them.
                    If None (default), auto-detect based on current platform.

    Returns:
        Sanitized directory name safe for the target platform
    """
    if for_windows is None:
        for_windows = is_windows()

    if not for_windows:
        return dirname

    # Replace invalid characters
    dirname = WINDOWS_INVALID_CHARS.sub("_", dirname)

    # Remove leading/trailing spaces and dots
    dirname = dirname.strip(" .")

    # Check for reserved names
    if dirname.upper() in WINDOWS_RESERVED_NAMES:
        dirname = dirname + "_dir"

    # Truncate if too long
    if len(dirname) > WINDOWS_SAFE_FILENAME_LENGTH:
        dirname = dirname[:WINDOWS_SAFE_FILENAME_LENGTH]

    return dirname


def get_platform_info() -> dict:
    """Get information about the current platform."""
    return {
        "platform": sys.platform,
        "is_windows": is_windows(),
        "is_macos": is_macos(),
        "is_linux": is_linux(),
        "max_filename_length": WINDOWS_SAFE_FILENAME_LENGTH if is_windows() else MAX_FILENAME_LENGTH,
    }


# Regex patterns for extracting dates from filenames
DATE_PATTERNS = [
    # YYYY-MM-DD or YYYY_MM_DD
    (re.compile(r'(\d{4})[-_](\d{2})[-_](\d{2})'), lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),
    # YYYYMMDD
    (re.compile(r'(\d{4})(\d{2})(\d{2})'), lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),
    # MMDDYYYY
    (re.compile(r'(\d{2})(\d{2})(\d{4})'), lambda m: (int(m.group(3)), int(m.group(1)), int(m.group(2)))),
    # YYYYMM (use first of month)
    (re.compile(r'(\d{4})(\d{2})(?!\d)'), lambda m: (int(m.group(1)), int(m.group(2)), 1)),
    # Q1-Q4_YYYY
    (re.compile(r'Q([1-4])[-_](\d{4})'), lambda m: (int(m.group(2)), int(m.group(1)) * 3, 15)),
]


def extract_date_from_filename(filename: str) -> datetime | None:
    """
    Extract a date from a filename if one is present.

    Args:
        filename: The filename to parse

    Returns:
        datetime object if a date was found, None otherwise
    """
    for pattern, extractor in DATE_PATTERNS:
        match = pattern.search(filename)
        if match:
            try:
                year, month, day = extractor(match)
                # Validate the date
                if 2000 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                    # Clamp day to valid range for the month
                    if month in (4, 6, 9, 11) and day > 30:
                        day = 30
                    elif month == 2 and day > 28:
                        day = 28
                    return datetime(year, month, day)
            except (ValueError, IndexError):
                continue
    return None


def generate_realistic_timestamp(
    filename: str,
    base_date: datetime | None = None,
) -> tuple[float, float]:
    """
    Generate realistic atime and mtime timestamps for a file.

    Args:
        filename: The filename (used to extract embedded dates)
        base_date: Optional base date to use if no date in filename

    Returns:
        Tuple of (atime, mtime) as Unix timestamps
    """
    # Try to extract date from filename
    file_date = extract_date_from_filename(filename)

    if file_date is None:
        # No date in filename - generate random date within last 2 years
        if base_date is None:
            base_date = datetime.now()
        days_ago = random.randint(1, 730)  # Up to 2 years ago
        file_date = base_date - timedelta(days=days_ago)

    # Add random time of day (business hours more likely)
    if random.random() < 0.8:
        # Business hours: 8am - 6pm
        hour = random.randint(8, 17)
    else:
        # Off hours
        hour = random.choice(list(range(0, 8)) + list(range(18, 24)))

    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    file_datetime = file_date.replace(hour=hour, minute=minute, second=second)

    # mtime is the "modified" time
    mtime = file_datetime.timestamp()

    # atime (access time) is typically same or slightly after mtime
    # Simulate that file was accessed sometime after creation
    access_delta = random.randint(0, 86400 * 30)  # Up to 30 days later
    atime = mtime + access_delta

    # Don't let atime be in the future
    now = datetime.now().timestamp()
    if atime > now:
        atime = now

    return atime, mtime


def set_file_timestamp(
    filepath: Path | str,
    atime: float | None = None,
    mtime: float | None = None,
) -> None:
    """
    Set the access and modification times of a file.

    Args:
        filepath: Path to the file
        atime: Access time as Unix timestamp (None = use mtime)
        mtime: Modification time as Unix timestamp (None = generate from filename)
    """
    filepath = Path(filepath)

    if not filepath.exists():
        return

    if mtime is None:
        atime, mtime = generate_realistic_timestamp(filepath.name)
    elif atime is None:
        atime = mtime

    os.utime(filepath, (atime, mtime))
