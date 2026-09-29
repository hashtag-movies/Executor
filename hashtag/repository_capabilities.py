
"""Hashtag Gate 9 Step 4: repository capability I/O contracts.

This module extends the generic Gate 9 repository capabilities with concrete
input/output contracts so the existing Hashtag capability planner can compose
repository operations through actual data-flow constraints.

It does not execute repository operations and does not introduce another
planner, executor, verifier, or learning system.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .capability_manifest import CapabilityManifest, CapabilitySpec


VERSION = "2.1-G9-S4"


def _field(
    name: str,
    type_name: str = "any",
    *,
    required: bool = False,
    description: str = "",
) -> Dict[str, Any]:
    return {
        "name": name,
        "type": type_name,
        "required": required,
        "description": description,
    }


REPOSITORY_READ_CAPABILITIES: List[CapabilitySpec] = [
    CapabilitySpec(
        capability_id="repository.identify",
        description="Identify a repository and return stable repository metadata.",
        input_schema={
            "fields": [
                _field(
                    "repository",
                    "string",
                    required=True,
                    description="Repository location, identifier, or authorized reference.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "identity",
                    "object",
                    required=True,
                    description="Stable repository identity.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "identify", "inspect", "read"],
        side_effects=[],
        risk_level="low",
        consumes=["repository.reference"],
        produces=["repository.identity"],
    ),
    CapabilitySpec(
        capability_id="repository.inspect",
        description="Inspect repository state, structure, revision, and metadata.",
        input_schema={
            "fields": [
                _field(
                    "identity",
                    "object",
                    required=True,
                    description="Repository identity from identification.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "inspection",
                    "object",
                    required=True,
                    description="Repository inspection snapshot.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "inspect", "read", "structure"],
        side_effects=[],
        risk_level="low",
        consumes=["repository.identity"],
        produces=["repository.inspection"],
    ),
    CapabilitySpec(
        capability_id="repository.list_files",
        description="List files and directories available in a repository.",
        input_schema={
            "fields": [
                _field(
                    "identity",
                    "object",
                    required=True,
                    description="Repository identity.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "entries",
                    "array",
                    required=True,
                    description="Repository files and directories.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "files", "directories", "list", "read"],
        side_effects=[],
        risk_level="low",
        consumes=["repository.identity"],
        produces=["repository.entries"],
    ),
    CapabilitySpec(
        capability_id="repository.read_file",
        description="Read the contents of a file in a repository.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
                _field(
                    "path",
                    "string",
                    required=True,
                    description="Repository-relative file path.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "file_content",
                    "string",
                    required=True,
                    description="Contents of the requested file.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "file", "read", "source"],
        side_effects=[],
        risk_level="low",
        consumes=["repository.identity", "repository.path"],
        produces=["repository.file_content"],
    ),
    CapabilitySpec(
        capability_id="repository.search",
        description="Search repository files or source content.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
                _field(
                    "query",
                    "string",
                    required=True,
                    description="Search query.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "search_results",
                    "array",
                    required=True,
                    description="Matching repository locations or content.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "search", "code", "text", "read"],
        side_effects=[],
        risk_level="low",
        consumes=["repository.identity", "repository.query"],
        produces=["repository.search_results"],
    ),
    CapabilitySpec(
        capability_id="repository.list_branches",
        description="List branches or equivalent repository references.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "branches",
                    "array",
                    required=True,
                    description="Available branches or references.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "branches", "refs", "list", "read"],
        side_effects=[],
        risk_level="low",
        consumes=["repository.identity"],
        produces=["repository.branches"],
    ),
    CapabilitySpec(
        capability_id="repository.inspect_branch",
        description="Inspect a repository branch or reference.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
                _field(
                    "branch",
                    "string",
                    required=True,
                    description="Branch or reference name.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "branch_state",
                    "object",
                    required=True,
                    description="Branch state and revision information.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "branch", "inspect", "revision", "read"],
        side_effects=[],
        risk_level="low",
        consumes=["repository.identity", "repository.branch"],
        produces=["repository.branch_state"],
    ),
    CapabilitySpec(
        capability_id="repository.list_history",
        description="List repository history or commits.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "history",
                    "array",
                    required=True,
                    description="Repository history records.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "history", "commits", "log", "read"],
        side_effects=[],
        risk_level="low",
        consumes=["repository.identity"],
        produces=["repository.history"],
    ),
]


REPOSITORY_WRITE_CAPABILITIES: List[CapabilitySpec] = [
    CapabilitySpec(
        capability_id="repository.create_branch",
        description="Create an isolated branch or equivalent workspace reference.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
                _field(
                    "branch",
                    "string",
                    required=True,
                    description="Requested isolated branch name.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "branch",
                    "string",
                    required=True,
                    description="Created branch name.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "branch", "create", "write"],
        side_effects=["creates_branch"],
        risk_level="medium",
        consumes=["repository.identity"],
        produces=["repository.branch"],
    ),
    CapabilitySpec(
        capability_id="repository.write_file",
        description="Create or modify a file in a repository workspace.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
                _field(
                    "path",
                    "string",
                    required=True,
                    description="Repository-relative target file path.",
                ),
                _field(
                    "file_content",
                    "string",
                    required=True,
                    description="New file content.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "modified_workspace",
                    "object",
                    required=True,
                    description="Workspace state after modification.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "file", "write", "modify"],
        side_effects=["modifies_files"],
        risk_level="high",
        consumes=[
            "repository.identity",
            "repository.path",
            "repository.file_content",
        ],
        produces=["repository.modified_workspace"],
    ),
    CapabilitySpec(
        capability_id="repository.run_command",
        description="Run a repository-local command in an authorized workspace.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
                _field(
                    "command",
                    "string",
                    required=True,
                    description="Authorized repository-local command.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "command_result",
                    "object",
                    required=True,
                    description="Command execution result.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "command", "execute", "terminal", "build", "test"],
        side_effects=["executes_command"],
        risk_level="medium",
        consumes=["repository.identity", "repository.command"],
        produces=["repository.command_result"],
    ),
    CapabilitySpec(
        capability_id="repository.run_tests",
        description="Run the repository's available test suite or test command.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "test_result",
                    "object",
                    required=True,
                    description="Test execution result.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "test", "tests", "verify", "execute"],
        side_effects=["executes_tests"],
        risk_level="medium",
        consumes=["repository.identity"],
        produces=["repository.test_result"],
    ),
    CapabilitySpec(
        capability_id="repository.commit",
        description="Create a repository commit from authorized workspace changes.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
                _field(
                    "modified_workspace",
                    "object",
                    required=True,
                    description="Authorized modified workspace state.",
                ),
                _field(
                    "message",
                    "string",
                    required=True,
                    description="Commit message.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "commit",
                    "object",
                    required=True,
                    description="Created commit information.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "commit", "write", "history"],
        side_effects=["creates_commit"],
        risk_level="high",
        consumes=["repository.identity", "repository.modified_workspace"],
        produces=["repository.commit"],
    ),
    CapabilitySpec(
        capability_id="repository.create_pull_request",
        description="Create a pull request or equivalent review request.",
        input_schema={
            "fields": [
                _field("identity", "object", required=True),
                _field(
                    "branch",
                    "string",
                    required=True,
                    description="Source branch for review.",
                ),
                _field(
                    "title",
                    "string",
                    required=True,
                    description="Review request title.",
                ),
            ],
            "allow_extra": True,
        },
        output_schema={
            "fields": [
                _field(
                    "pull_request",
                    "object",
                    required=True,
                    description="Created review request information.",
                ),
            ],
            "allow_extra": True,
        },
        tags=["repository", "pull_request", "review", "write"],
        side_effects=["creates_review_request"],
        risk_level="high",
        consumes=["repository.identity", "repository.branch"],
        produces=["repository.pull_request"],
    ),
]


def repository_capabilities(
    *,
    include_write: bool = True,
) -> List[CapabilitySpec]:
    """Return fresh provider-neutral repository capability specifications."""

    capabilities = list(REPOSITORY_READ_CAPABILITIES)

    if include_write:
        capabilities.extend(REPOSITORY_WRITE_CAPABILITIES)

    return capabilities


def build_repository_manifest(
    *,
    body_id: str,
    name: str,
    version: str = VERSION,
    protocol_version: str = "1.0",
    include_write: bool = True,
    metadata: Dict[str, Any] | None = None,
) -> CapabilityManifest:
    """Build a repository Body manifest using the existing capability system."""

    return CapabilityManifest(
        body_id=body_id,
        name=name,
        version=version,
        protocol_version=protocol_version,
        capabilities=repository_capabilities(
            include_write=include_write,
        ),
        description="Provider-neutral repository capabilities for Hashtag Bodies.",
        metadata=metadata or {},
    )


__all__ = [
    "VERSION",
    "REPOSITORY_READ_CAPABILITIES",
    "REPOSITORY_WRITE_CAPABILITIES",
    "repository_capabilities",
    "build_repository_manifest",
]
