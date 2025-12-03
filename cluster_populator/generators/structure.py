"""Directory structure generator for business file hierarchies."""

import random
from pathlib import Path
from dataclasses import dataclass

from .filenames import FilenameGenerator


@dataclass
class FileSpec:
    """Specification for a file to be generated."""
    path: Path
    extension: str
    content_type: str
    department: str


class StructureGenerator:
    """Generate realistic business directory structures."""

    DEPARTMENT_WEIGHTS = {
        "Finance": 15,
        "Human_Resources": 12,
        "Marketing": 15,
        "Sales": 18,
        "Operations": 12,
        "Legal": 8,
        "IT": 12,
        "Executive": 8,
    }

    def __init__(self, seed: int | None = None, sanitize_for_windows: bool | None = None):
        """
        Initialize structure generator.

        Args:
            seed: Random seed for reproducibility
            sanitize_for_windows: If True, sanitize names for Windows. If False, skip.
                                 If None (default), auto-detect based on current platform.
        """
        self.filename_gen = FilenameGenerator(seed=seed, sanitize_for_windows=sanitize_for_windows)
        if seed is not None:
            random.seed(seed)

    def generate_structure(
        self,
        base_path: Path,
        total_files: int,
        depth: int = 2,
    ) -> list[FileSpec]:
        """
        Generate a directory structure with file specifications.

        Args:
            base_path: Root directory for the file structure
            total_files: Total number of files to generate
            depth: How deep subdirectories should go (1-3)

        Returns:
            List of FileSpec objects describing files to create
        """
        depth = max(1, min(3, depth))
        departments = self.filename_gen.get_departments()
        dept_weights = [self.DEPARTMENT_WEIGHTS.get(d, 10) for d in departments]

        file_specs = []
        files_per_dept = self._distribute_files(total_files, departments, dept_weights)

        for dept, count in files_per_dept.items():
            dept_path = base_path / dept

            if depth >= 2:
                subdirs = self.filename_gen.SUBDIRECTORIES.get(dept, [])
                if subdirs:
                    subdir_allocation = self._distribute_to_subdirs(count, subdirs)
                    for subdir, subdir_count in subdir_allocation.items():
                        subdir_path = dept_path / subdir

                        if depth >= 3 and subdir_count > 5:
                            year_allocation = self._distribute_by_year(subdir_count)
                            for year, year_count in year_allocation.items():
                                year_path = subdir_path / year
                                for _ in range(year_count):
                                    spec = self._create_file_spec(year_path, dept)
                                    file_specs.append(spec)
                        else:
                            for _ in range(subdir_count):
                                spec = self._create_file_spec(subdir_path, dept)
                                file_specs.append(spec)
                else:
                    for _ in range(count):
                        spec = self._create_file_spec(dept_path, dept)
                        file_specs.append(spec)
            else:
                for _ in range(count):
                    spec = self._create_file_spec(dept_path, dept)
                    file_specs.append(spec)

        return file_specs

    def _distribute_files(
        self,
        total: int,
        departments: list[str],
        weights: list[int],
    ) -> dict[str, int]:
        """Distribute files across departments based on weights."""
        total_weight = sum(weights)
        distribution = {}

        remaining = total
        for i, dept in enumerate(departments[:-1]):
            count = int(total * weights[i] / total_weight)
            count = max(1, count) if remaining > len(departments) - i else 0
            distribution[dept] = min(count, remaining)
            remaining -= distribution[dept]

        distribution[departments[-1]] = remaining

        return {k: v for k, v in distribution.items() if v > 0}

    def _distribute_to_subdirs(self, count: int, subdirs: list[str]) -> dict[str, int]:
        """Distribute files across subdirectories."""
        if count <= len(subdirs):
            selected = random.sample(subdirs, count)
            return {s: 1 for s in selected}

        distribution = {}
        remaining = count
        num_subdirs = min(len(subdirs), max(2, count // 3))
        selected_subdirs = random.sample(subdirs, num_subdirs)

        for i, subdir in enumerate(selected_subdirs[:-1]):
            avg = remaining // (num_subdirs - i)
            variance = max(1, avg // 3)
            subdir_count = random.randint(max(1, avg - variance), avg + variance)
            subdir_count = min(subdir_count, remaining - (num_subdirs - i - 1))
            distribution[subdir] = subdir_count
            remaining -= subdir_count

        distribution[selected_subdirs[-1]] = remaining

        return distribution

    def _distribute_by_year(self, count: int) -> dict[str, int]:
        """Distribute files by year."""
        current_year = 2024
        years = [str(y) for y in range(current_year - 2, current_year + 1)]

        weights = [1, 2, 4]
        total_weight = sum(weights)

        distribution = {}
        remaining = count

        for i, year in enumerate(years[:-1]):
            year_count = int(count * weights[i] / total_weight)
            year_count = max(0, min(year_count, remaining - (len(years) - i - 1)))
            if year_count > 0:
                distribution[year] = year_count
                remaining -= year_count

        if remaining > 0:
            distribution[years[-1]] = remaining

        return distribution

    def _create_file_spec(self, directory: Path, department: str) -> FileSpec:
        """Create a file specification."""
        filename, content_type = self.filename_gen.generate_filename(department)
        extension = Path(filename).suffix

        return FileSpec(
            path=directory / filename,
            extension=extension,
            content_type=content_type,
            department=department,
        )

    def get_directory_tree(self, base_path: Path, file_specs: list[FileSpec]) -> str:
        """Generate a visual directory tree representation."""
        directories = set()
        for spec in file_specs:
            parent = spec.path.parent
            while parent != base_path and parent != parent.parent:
                directories.add(parent)
                parent = parent.parent

        sorted_dirs = sorted(directories)

        lines = [str(base_path)]
        for directory in sorted_dirs:
            rel_path = directory.relative_to(base_path)
            depth = len(rel_path.parts)
            indent = "  " * depth
            lines.append(f"{indent}{rel_path.parts[-1]}/")

        return "\n".join(lines)
