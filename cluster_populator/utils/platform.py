"""Platform detection and path sanitization utilities."""

import re
import sys


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
