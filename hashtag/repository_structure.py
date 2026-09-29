
"""Hashtag Gate 9 Step 3: repository structure and project-type detection.

This module analyzes repository inspection evidence and produces a
provider-neutral structural description.

It does not execute commands, modify repositories, or contain planning logic.
Detection is evidence-based and supports repositories containing multiple
project types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple

from .repository_contract import RepositoryInspection


VERSION = "2.1-G9-S3"


@dataclass(frozen=True)
class StructureEvidence:
    """One observed fact supporting a project-type classification."""

    path: str
    reason: str
    project_type: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "reason": self.reason,
            "project_type": self.project_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructureEvidence":
        return cls(
            path=str(data.get("path", "")),
            reason=str(data.get("reason", "")),
            project_type=str(data.get("project_type", "")),
        )


@dataclass
class ProjectType:
    """A detected project type with evidence and confidence."""

    name: str
    confidence: float
    evidence: List[StructureEvidence] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = str(self.name).strip()
        self.confidence = max(0.0, min(1.0, float(self.confidence)))

        if not self.name:
            raise ValueError("project type name is required")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "confidence": self.confidence,
            "evidence": [item.as_dict() for item in self.evidence],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectType":
        return cls(
            name=data.get("name", ""),
            confidence=data.get("confidence", 0.0),
            evidence=[
                StructureEvidence.from_dict(item)
                for item in data.get("evidence", [])
            ],
        )


@dataclass
class RepositoryStructure:
    """Provider-neutral structural understanding of a repository."""

    project_types: List[ProjectType] = field(default_factory=list)
    root_files: List[str] = field(default_factory=list)
    root_directories: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    build_systems: List[str] = field(default_factory=list)
    test_indicators: List[str] = field(default_factory=list)
    package_managers: List[str] = field(default_factory=list)
    evidence: List[StructureEvidence] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    VERSION = VERSION

    def has_project_type(self, name: str) -> bool:
        target = str(name).strip().lower()
        return any(item.name.lower() == target for item in self.project_types)

    def project_type_names(self) -> List[str]:
        return [item.name for item in self.project_types]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.VERSION,
            "project_types": [item.as_dict() for item in self.project_types],
            "root_files": list(self.root_files),
            "root_directories": list(self.root_directories),
            "languages": list(self.languages),
            "build_systems": list(self.build_systems),
            "test_indicators": list(self.test_indicators),
            "package_managers": list(self.package_managers),
            "evidence": [item.as_dict() for item in self.evidence],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryStructure":
        return cls(
            project_types=[
                ProjectType.from_dict(item)
                for item in data.get("project_types", [])
            ],
            root_files=list(data.get("root_files", [])),
            root_directories=list(data.get("root_directories", [])),
            languages=list(data.get("languages", [])),
            build_systems=list(data.get("build_systems", [])),
            test_indicators=list(data.get("test_indicators", [])),
            package_managers=list(data.get("package_managers", [])),
            evidence=[
                StructureEvidence.from_dict(item)
                for item in data.get("evidence", [])
            ],
            metadata=data.get("metadata") or {},
        )


class RepositoryStructureDetector:
    """Detect project structure from repository inspection evidence."""

    VERSION = VERSION

    _MARKERS: Dict[
        str,
        Tuple[str, str, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]],
    ] = {
        "pyproject.toml": (
            "Python",
            "Python project configuration file",
            ("Python",),
            (),
            (),
        ),
        "setup.py": (
            "Python",
            "Python packaging configuration file",
            ("Python",),
            (),
            (),
        ),
        "requirements.txt": (
            "Python",
            "Python dependency manifest",
            ("Python",),
            (),
            ("pip",),
        ),
        "package.json": (
            "Node.js",
            "Node package manifest",
            ("JavaScript", "TypeScript"),
            (),
            ("npm",),
        ),
        "package-lock.json": (
            "Node.js",
            "npm lockfile",
            ("JavaScript", "TypeScript"),
            (),
            ("npm",),
        ),
        "yarn.lock": (
            "Node.js",
            "Yarn lockfile",
            ("JavaScript", "TypeScript"),
            (),
            ("Yarn",),
        ),
        "pnpm-lock.yaml": (
            "Node.js",
            "pnpm lockfile",
            ("JavaScript", "TypeScript"),
            (),
            ("pnpm",),
        ),
        "cargo.toml": (
            "Rust",
            "Rust package manifest",
            ("Rust",),
            ("Cargo",),
            (),
        ),
        "go.mod": (
            "Go",
            "Go module definition",
            ("Go",),
            ("Go Modules",),
            (),
        ),
        "pom.xml": (
            "Java",
            "Maven project descriptor",
            ("Java",),
            ("Maven",),
            (),
        ),
        "build.gradle": (
            "Java/JVM",
            "Gradle build configuration",
            ("Java",),
            ("Gradle",),
            (),
        ),
        "build.gradle.kts": (
            "Kotlin/JVM",
            "Gradle Kotlin build configuration",
            ("Kotlin",),
            ("Gradle",),
            (),
        ),
        "composer.json": (
            "PHP",
            "Composer package manifest",
            ("PHP",),
            (),
            ("Composer",),
        ),
        "gemfile": (
            "Ruby",
            "Ruby dependency manifest",
            ("Ruby",),
            (),
            ("Bundler",),
        ),
        "mix.exs": (
            "Elixir",
            "Elixir Mix project file",
            ("Elixir",),
            ("Mix",),
            (),
        ),
        "pubspec.yaml": (
            "Dart/Flutter",
            "Dart package manifest",
            ("Dart",),
            (),
            ("pub",),
        ),
        "dockerfile": (
            "Docker",
            "Docker build definition",
            (),
            ("Docker",),
            (),
        ),
        "docker-compose.yml": (
            "Docker Compose",
            "Docker Compose configuration",
            (),
            ("Docker Compose",),
            (),
        ),
        "docker-compose.yaml": (
            "Docker Compose",
            "Docker Compose configuration",
            (),
            ("Docker Compose",),
            (),
        ),
    }

    _EXTENSIONS: Dict[str, Tuple[str, str]] = {
        ".py": ("Python", "Python source file"),
        ".js": ("JavaScript", "JavaScript source file"),
        ".jsx": ("JavaScript/React", "JSX source file"),
        ".ts": ("TypeScript", "TypeScript source file"),
        ".tsx": ("TypeScript/React", "TSX source file"),
        ".rs": ("Rust", "Rust source file"),
        ".go": ("Go", "Go source file"),
        ".java": ("Java", "Java source file"),
        ".kt": ("Kotlin", "Kotlin source file"),
        ".kts": ("Kotlin", "Kotlin source file"),
        ".cs": ("C#", "C# source file"),
        ".cpp": ("C++", "C++ source file"),
        ".cc": ("C++", "C++ source file"),
        ".c": ("C", "C source file"),
        ".h": ("C/C++", "C/C++ header file"),
        ".hpp": ("C++", "C++ header file"),
        ".php": ("PHP", "PHP source file"),
        ".rb": ("Ruby", "Ruby source file"),
        ".swift": ("Swift", "Swift source file"),
        ".dart": ("Dart", "Dart source file"),
        ".ex": ("Elixir", "Elixir source file"),
        ".exs": ("Elixir", "Elixir source file"),
    }

    _TEST_MARKERS = {
        "pytest.ini",
        "tox.ini",
        "jest.config.js",
        "jest.config.ts",
        "vitest.config.js",
        "vitest.config.ts",
        "cargo.toml",
        "go.mod",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
    }

    _TEST_DIRECTORIES = {
        "test",
        "tests",
        "__tests__",
        "spec",
        "specs",
    }

    def detect(self, inspection: RepositoryInspection) -> RepositoryStructure:
        """Detect structure from a repository inspection snapshot."""

        if not isinstance(inspection, RepositoryInspection):
            raise TypeError("inspection must be a RepositoryInspection")

        entries = inspection.entries

        root_files: List[str] = []
        root_directories: List[str] = []

        for entry in entries:
            normalized = entry.path.replace("\\", "/").strip("/")

            if not normalized:
                continue

            parts = normalized.split("/")

            if len(parts) == 1:
                if entry.kind == "directory":
                    root_directories.append(parts[0])
                elif entry.kind == "file":
                    root_files.append(parts[0])

        root_files = _unique(root_files)
        root_directories = _unique(root_directories)

        evidence: List[StructureEvidence] = []

        # Marker-based detection.
        for entry in entries:
            filename = (
                entry.path.replace("\\", "/")
                .rstrip("/")
                .split("/")[-1]
            )

            marker = self._MARKERS.get(filename.lower())

            if marker:
                project_type, reason, _, _, _ = marker

                evidence.append(
                    StructureEvidence(
                        path=entry.path,
                        reason=reason,
                        project_type=project_type,
                    )
                )

        # Extension-based detection.
        for entry in entries:
            if entry.kind != "file":
                continue

            path = entry.path.replace("\\", "/")
            filename = path.split("/")[-1].lower()

            if "." not in filename:
                continue

            extension = "." + filename.rsplit(".", 1)[1]
            extension_info = self._EXTENSIONS.get(extension)

            if extension_info:
                project_type, reason = extension_info

                evidence.append(
                    StructureEvidence(
                        path=entry.path,
                        reason=reason,
                        project_type=project_type,
                    )
                )

        languages: List[str] = []
        build_systems: List[str] = []
        package_managers: List[str] = []

        for item in evidence:
            marker = self._MARKER_FOR_EVIDENCE(item)

            if marker:
                _, _, marker_languages, marker_builds, marker_packages = marker
                languages.extend(marker_languages)
                build_systems.extend(marker_builds)
                package_managers.extend(marker_packages)

            extension = self._EXTENSION_FOR_PATH(item.path)

            if extension:
                language, _ = extension
                languages.append(language)

        # Test evidence can occur anywhere in the repository, not only
        # at the root. Detect both marker files and directory components.
        test_indicators: List[str] = []

        for entry in entries:
            normalized = entry.path.replace("\\", "/").strip("/")

            if not normalized:
                continue

            parts = normalized.split("/")
            filename = parts[-1].lower()

            if filename in self._TEST_MARKERS:
                test_indicators.append(entry.path)

            for directory in parts[:-1]:
                if directory.lower() in self._TEST_DIRECTORIES:
                    test_indicators.append(directory)
                    break

        languages = _unique(languages)
        build_systems = _unique(build_systems)
        package_managers = _unique(package_managers)
        test_indicators = _unique(test_indicators)

        grouped: Dict[str, List[StructureEvidence]] = {}

        for item in evidence:
            grouped.setdefault(item.project_type, []).append(item)

        project_types: List[ProjectType] = []

        for name, items in grouped.items():
            confidence = self._confidence(name, items)

            project_types.append(
                ProjectType(
                    name=name,
                    confidence=confidence,
                    evidence=list(items),
                )
            )

        project_types.sort(
            key=lambda item: (-item.confidence, item.name.lower())
        )

        return RepositoryStructure(
            project_types=project_types,
            root_files=root_files,
            root_directories=root_directories,
            languages=languages,
            build_systems=build_systems,
            test_indicators=test_indicators,
            package_managers=package_managers,
            evidence=evidence,
            metadata={
                "inspection_version": inspection.VERSION,
                "detector_version": self.VERSION,
            },
        )

    def _confidence(
        self,
        project_type: str,
        evidence: Iterable[StructureEvidence],
    ) -> float:
        items = list(evidence)

        if not items:
            return 0.0

        marker_count = sum(
            1
            for item in items
            if (
                item.path.replace("\\", "/")
                .rstrip("/")
                .split("/")[-1]
                .lower()
                in self._MARKERS
            )
        )

        score = min(1.0, 0.35 * len(items) + 0.25 * marker_count)

        if len(items) == 1 and marker_count == 0:
            score = 0.35

        return round(min(1.0, score), 3)

    def _MARKER_FOR_EVIDENCE(
        self,
        evidence: StructureEvidence,
    ):
        filename = (
            evidence.path.replace("\\", "/")
            .rstrip("/")
            .split("/")[-1]
            .lower()
        )

        return self._MARKERS.get(filename)

    def _EXTENSION_FOR_PATH(self, path: str):
        filename = path.replace("\\", "/").split("/")[-1].lower()

        if "." not in filename:
            return None

        extension = "." + filename.rsplit(".", 1)[1]

        return self._EXTENSIONS.get(extension)


def _unique(values: Iterable[str]) -> List[str]:
    result: List[str] = []
    seen = set()

    for value in values:
        text = str(value).strip()

        if text and text.lower() not in seen:
            seen.add(text.lower())
            result.append(text)

    return result


__all__ = [
    "VERSION",
    "StructureEvidence",
    "ProjectType",
    "RepositoryStructure",
    "RepositoryStructureDetector",
]
