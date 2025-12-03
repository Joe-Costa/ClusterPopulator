"""Command-line interface for ClusterPopulator."""

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .orchestrator import Orchestrator
from .utils.platform import get_platform_info, is_windows


def create_progress_bar(current: int, total: int, width: int = 40) -> str:
    """Create a text-based progress bar."""
    percentage = current / total if total > 0 else 0
    filled = int(width * percentage)
    bar = "=" * filled + "-" * (width - filled)
    return f"[{bar}] {current}/{total} ({percentage * 100:.1f}%)"


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="cluster-populator",
        description="Generate realistic business file structures with sample data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate 100 files in ./test_data:
    python -m cluster_populator ./test_data 100

  Generate 500 files with deep structure:
    python -m cluster_populator /path/to/output 500 --depth 3

  Preview without creating files:
    python -m cluster_populator ./output 50 --preview

  Use a seed for reproducible output:
    python -m cluster_populator ./output 100 --seed 12345

  Force Windows-compatible filenames (for generating on Mac/Linux for Windows):
    python -m cluster_populator ./output 100 --windows
""",
    )

    parser.add_argument(
        "path",
        type=str,
        help="Output directory path for generated files",
    )

    parser.add_argument(
        "count",
        type=int,
        help="Number of files to generate",
    )

    parser.add_argument(
        "-d", "--depth",
        type=int,
        default=2,
        choices=[1, 2, 3],
        help="Directory depth (1=flat, 2=with subdirs, 3=with years). Default: 2",
    )

    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible output",
    )

    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=10,
        help="Maximum concurrent file generation tasks. Default: 10",
    )

    parser.add_argument(
        "-p", "--preview",
        action="store_true",
        help="Preview structure without creating files",
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    parser.add_argument(
        "-w", "--windows",
        action="store_true",
        help="Force Windows-compatible filenames (auto-detected on Windows)",
    )

    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Disable realistic file timestamps (timestamps enabled by default)",
    )

    parser.add_argument(
        "--platform-info",
        action="store_true",
        help="Show platform information and exit",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Handle --platform-info
    if args.platform_info:
        info = get_platform_info()
        print("Platform Information:")
        print(f"  Platform: {info['platform']}")
        print(f"  Is Windows: {info['is_windows']}")
        print(f"  Is macOS: {info['is_macos']}")
        print(f"  Is Linux: {info['is_linux']}")
        print(f"  Max filename length: {info['max_filename_length']}")
        print(f"\nFilename sanitization: {'enabled' if info['is_windows'] else 'disabled (use --windows to force)'}")
        return 0

    if args.count < 1:
        print("Error: count must be at least 1", file=sys.stderr)
        return 1

    if args.count > 10000:
        print("Error: count cannot exceed 10000", file=sys.stderr)
        return 1

    output_path = Path(args.path).resolve()

    if output_path.exists() and not output_path.is_dir():
        print(f"Error: {output_path} exists and is not a directory", file=sys.stderr)
        return 1

    progress_state = {"last_update": 0}

    def progress_callback(current: int, total: int) -> None:
        if args.quiet:
            return
        now = time.time()
        if now - progress_state["last_update"] >= 0.1 or current == total:
            progress_state["last_update"] = now
            bar = create_progress_bar(current, total)
            print(f"\r{bar}", end="", flush=True)
            if current == total:
                print()

    # Determine Windows sanitization mode
    # --windows flag forces it on, otherwise auto-detect
    sanitize_for_windows = True if args.windows else None

    # Timestamps enabled by default, --no-timestamps disables
    realistic_timestamps = not args.no_timestamps

    orchestrator = Orchestrator(
        seed=args.seed,
        concurrency=args.concurrency,
        progress_callback=progress_callback,
        sanitize_for_windows=sanitize_for_windows,
        realistic_timestamps=realistic_timestamps,
    )

    if args.preview:
        if not args.quiet:
            print(f"Preview of structure for {args.count} files in {output_path}:\n")

        file_specs, tree = orchestrator.preview_structure(
            base_path=output_path,
            total_files=args.count,
            depth=args.depth,
        )

        print("Directory structure:")
        print(tree)
        print()

        ext_counts = {}
        dept_counts = {}
        for spec in file_specs:
            ext_counts[spec.extension] = ext_counts.get(spec.extension, 0) + 1
            dept_counts[spec.department] = dept_counts.get(spec.department, 0) + 1

        print("Files by extension:")
        for ext, count in sorted(ext_counts.items(), key=lambda x: -x[1]):
            print(f"  {ext}: {count}")

        print("\nFiles by department:")
        for dept, count in sorted(dept_counts.items(), key=lambda x: -x[1]):
            print(f"  {dept}: {count}")

        return 0

    if not args.quiet:
        print(f"Generating {args.count} files in {output_path}")
        print(f"Depth: {args.depth}, Concurrency: {args.concurrency}")
        if args.seed:
            print(f"Seed: {args.seed}")
        if args.windows:
            print("Windows filename sanitization: enabled (forced)")
        elif is_windows():
            print("Windows filename sanitization: enabled (auto-detected)")
        if not args.no_timestamps:
            print("Realistic timestamps: enabled")
        print()

    start_time = time.time()

    result = orchestrator.generate_sync(
        base_path=output_path,
        total_files=args.count,
        depth=args.depth,
    )

    elapsed = time.time() - start_time

    if not args.quiet:
        print()
        print("Generation complete!")
        print(f"  Total files: {result.total_files}")
        print(f"  Successful: {result.successful}")
        print(f"  Failed: {result.failed}")
        print(f"  Directories created: {result.directories_created}")
        print(f"  Time elapsed: {elapsed:.2f}s")
        print(f"  Rate: {result.successful / elapsed:.1f} files/sec")

        if result.errors:
            print("\nErrors:")
            for path, error in result.errors[:10]:
                print(f"  {path}: {error}")
            if len(result.errors) > 10:
                print(f"  ... and {len(result.errors) - 10} more errors")

    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
