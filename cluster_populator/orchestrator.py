"""Async orchestrator for parallel file generation."""

import asyncio
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Callable

from .generators.content import ContentGenerator
from .generators.files import FileGenerator
from .generators.structure import StructureGenerator, FileSpec


@dataclass
class GenerationResult:
    """Result of file generation."""
    total_files: int
    successful: int
    failed: int
    errors: list[tuple[Path, str]]
    directories_created: int


class Orchestrator:
    """Orchestrate parallel file generation."""

    EXTENSION_GENERATORS = {
        ".txt": "generate_txt",
        ".json": "generate_json",
        ".csv": "generate_csv",
        ".docx": "generate_docx",
        ".xlsx": "generate_xlsx",
        ".pdf": "generate_pdf",
        ".pptx": "generate_pptx",
        ".xml": "generate_xml",
        ".html": "generate_html",
        ".md": "generate_md",
    }

    def __init__(
        self,
        seed: int | None = None,
        concurrency: int = 10,
        progress_callback: Callable[[int, int], None] | None = None,
        sanitize_for_windows: bool | None = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            seed: Random seed for reproducibility
            concurrency: Maximum concurrent file generation tasks
            progress_callback: Optional callback for progress updates (current, total)
            sanitize_for_windows: If True, sanitize filenames for Windows. If False, skip.
                                 If None (default), auto-detect based on current platform.
        """
        self.seed = seed
        self.concurrency = concurrency
        self.progress_callback = progress_callback
        self.sanitize_for_windows = sanitize_for_windows
        self.content_gen = ContentGenerator(seed=seed)
        self.file_gen = FileGenerator(content_gen=self.content_gen)
        self.structure_gen = StructureGenerator(seed=seed, sanitize_for_windows=sanitize_for_windows)

    async def generate(
        self,
        base_path: Path,
        total_files: int,
        depth: int = 2,
    ) -> GenerationResult:
        """
        Generate the complete file structure.

        Args:
            base_path: Root directory for file generation
            total_files: Total number of files to create
            depth: Directory depth (1-3)

        Returns:
            GenerationResult with statistics
        """
        base_path = Path(base_path).resolve()
        base_path.mkdir(parents=True, exist_ok=True)

        file_specs = self.structure_gen.generate_structure(
            base_path=base_path,
            total_files=total_files,
            depth=depth,
        )

        directories = set()
        for spec in file_specs:
            directories.add(spec.path.parent)

        for directory in sorted(directories):
            directory.mkdir(parents=True, exist_ok=True)

        semaphore = asyncio.Semaphore(self.concurrency)
        successful = 0
        failed = 0
        errors = []
        completed = 0

        async def generate_with_semaphore(spec: FileSpec) -> tuple[bool, Path, str | None]:
            nonlocal completed
            async with semaphore:
                try:
                    generator_method = self.EXTENSION_GENERATORS.get(spec.extension)
                    if generator_method:
                        method = getattr(self.file_gen, generator_method)
                        await method(spec.path, spec.content_type)
                        return True, spec.path, None
                    else:
                        await self.file_gen.generate_txt(spec.path, "memo")
                        return True, spec.path, None
                except Exception as e:
                    return False, spec.path, str(e)
                finally:
                    completed += 1
                    if self.progress_callback:
                        self.progress_callback(completed, len(file_specs))

        tasks = [generate_with_semaphore(spec) for spec in file_specs]
        results = await asyncio.gather(*tasks)

        for success, path, error in results:
            if success:
                successful += 1
            else:
                failed += 1
                errors.append((path, error or "Unknown error"))

        self.file_gen.shutdown()

        return GenerationResult(
            total_files=len(file_specs),
            successful=successful,
            failed=failed,
            errors=errors,
            directories_created=len(directories),
        )

    def generate_sync(
        self,
        base_path: Path,
        total_files: int,
        depth: int = 2,
    ) -> GenerationResult:
        """
        Synchronous wrapper for generate().

        Args:
            base_path: Root directory for file generation
            total_files: Total number of files to create
            depth: Directory depth (1-3)

        Returns:
            GenerationResult with statistics
        """
        return asyncio.run(self.generate(base_path, total_files, depth))

    def preview_structure(
        self,
        base_path: Path,
        total_files: int,
        depth: int = 2,
    ) -> tuple[list[FileSpec], str]:
        """
        Preview the structure that would be generated without creating files.

        Args:
            base_path: Root directory for file generation
            total_files: Total number of files to create
            depth: Directory depth (1-3)

        Returns:
            Tuple of (file_specs, directory_tree_string)
        """
        file_specs = self.structure_gen.generate_structure(
            base_path=Path(base_path).resolve(),
            total_files=total_files,
            depth=depth,
        )
        tree = self.structure_gen.get_directory_tree(
            Path(base_path).resolve(),
            file_specs,
        )
        return file_specs, tree
