"""
Hashtag Gate 9 Step 5: Real Repository Body Dispatch.

Thin provider-boundary adapter. The central Brain remains provider-neutral.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .contracts import Operation


class RepositoryBodyDispatchError(Exception):
    """Base error for repository Body dispatch."""


@dataclass(frozen=True)
class RepositoryOperationMapping:
    generic_operation: str
    provider_operation: str


class RepositoryBodyDispatch:
    VERSION = "2.1-G9-S5"

    GITHUB_OPERATIONS = {
        "repository.identify": "github.repository.inspect",
        "repository.inspect": "github.repository.inspect",
        "repository.list_files": "github.files.list",
        "repository.read_file": "github.file.read",
        "repository.search": "github.search.repositories",
        "repository.list_branches": "github.branches.list",
        "repository.inspect_branch": "github.branch.inspect",
        "repository.list_history": "github.commits.list",
        "repository.create_branch": "github.branch.create",
        "repository.write_file": "github.file.write",
        "repository.run_command": "github.run_command",
        "repository.run_tests": "github.run_tests",
        "repository.commit": "github.commit",
        "repository.create_pull_request": "github.pull_request.create",
    }

    @classmethod
    def mappings(cls) -> Dict[str, str]:
        return dict(cls.GITHUB_OPERATIONS)

    @classmethod
    def supports(cls, operation: Any) -> bool:
        return cls._operation_id(operation) in cls.GITHUB_OPERATIONS

    @classmethod
    def provider_operation(
        cls,
        operation: Any,
        *,
        provider: str = "github",
    ) -> str:
        operation_id = cls._operation_id(operation)
        provider_name = str(provider or "").strip().lower()

        if provider_name != "github":
            raise RepositoryBodyDispatchError(
                f"Unsupported repository provider: {provider}"
            )

        try:
            return cls.GITHUB_OPERATIONS[operation_id]
        except KeyError as exc:
            raise RepositoryBodyDispatchError(
                f"Unsupported repository operation: {operation_id}"
            ) from exc

    @classmethod
    def translate(
        cls,
        operation: Any,
        *,
        provider: str = "github",
    ) -> Operation:
        """
        Translate a structurally compatible operation into Core's Operation.

        The Executor Body has its own protocol.Operation type. Requiring that
        exact class here would create an unnecessary type coupling between the
        Core contract and the physical Body contract. We therefore consume the
        shared operation shape (operation + arguments) and return the Core
        Operation that represents the provider translation.
        """
        generic_operation = cls._operation_id(operation)
        if not generic_operation:
            raise RepositoryBodyDispatchError(
                "operation must provide a non-empty operation id"
            )

        raw_arguments = (
            operation.arguments
            if hasattr(operation, "arguments")
            else (
                operation.get("arguments", {})
                if isinstance(operation, dict)
                else {}
            )
        )
        arguments = dict(raw_arguments or {})

        provider_operation = cls.provider_operation(
            generic_operation,
            provider=provider,
        )

        if provider_name == "github":
            if provider_operation == "github.file.write":
                if "file" in arguments and "path" not in arguments:
                    arguments["path"] = arguments["file"]
                if "message" not in arguments:
                    arguments["message"] = f"Update {arguments.get('path', 'file')} via Hashtag"
            elif provider_operation in ("github.file.read", "github.file.delete"):
                if "file" in arguments and "path" not in arguments:
                    arguments["path"] = arguments["file"]

        dispatch_metadata = arguments.get("_repository_dispatch")
        if not isinstance(dispatch_metadata, dict):
            dispatch_metadata = {}
            arguments["_repository_dispatch"] = dispatch_metadata

        dispatch_metadata.update(
            {
                "version": cls.VERSION,
                "generic_operation": generic_operation,
                "provider": provider,
                "provider_operation": provider_operation,
            }
        )

        return Operation(
            operation=provider_operation,
            arguments=arguments,
        )

    @staticmethod
    def _operation_id(operation: Any) -> str:
        if isinstance(operation, Operation):
            value = operation.operation
        elif isinstance(operation, str):
            value = operation
        elif isinstance(operation, dict):
            value = (
                operation.get("operation")
                or operation.get("operation_id")
                or operation.get("id")
            )
        else:
            value = getattr(operation, "operation", "")

        return str(value or "").strip()


__all__ = [
    "RepositoryBodyDispatchError",
    "RepositoryOperationMapping",
    "RepositoryBodyDispatch",
]
