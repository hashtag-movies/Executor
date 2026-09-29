"""
Hashtag Core Body Router

V1.6

The Body Router selects a physical Body that advertises the
capability required by an already-planned Core operation.

The router does not understand natural language, create plans,
learn, verify, or execute physical operations itself.

Core remains the brain.
The Body remains responsible for physical execution and permissions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .body_client import BodyClient
from .contracts import Operation


class BodyRouterError(RuntimeError):
    """Base exception for Body Router failures."""


class NoBodyAvailableError(BodyRouterError):
    """Raised when no registered Body can perform an operation."""


@dataclass
class BodyInfo:
    """Information about a registered Body."""

    body_id: str
    name: str
    protocol_version: str
    version: str
    capabilities: set[str]
    client: BodyClient

    def supports(self, operation: str) -> bool:
        """Return True when this Body advertises the operation."""

        return operation in self.capabilities

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable Body description."""

        return {
            "body_id": self.body_id,
            "name": self.name,
            "protocol_version": self.protocol_version,
            "version": self.version,
            "capabilities": sorted(self.capabilities),
        }


class BodyRouter:
    """
    Routes already-planned Core operations to compatible Bodies.

    Bodies are registered dynamically from their live manifests.
    The router does not duplicate the Core planner.
    """

    def __init__(self) -> None:
        self._bodies: dict[str, BodyInfo] = {}

    # =========================================================
    # REGISTRATION
    # =========================================================

    def register(
        self,
        client: BodyClient,
        *,
        refresh: bool = True,
    ) -> BodyInfo:
        """
        Register a Body using its live manifest.

        The Body remains the source of truth for its capabilities.
        """

        if not isinstance(client, BodyClient):
            raise TypeError(
                "client must be hashtag.body_client.BodyClient"
            )

        if refresh:
            manifest = client.status()
        else:
            manifest = client.capabilities()

        body = self._parse_manifest(
            manifest,
            client,
        )

        self._bodies[body.body_id] = body

        return body

    def unregister(self, body_id: str) -> bool:
        """Remove a Body from the router."""

        return self._bodies.pop(
            body_id,
            None,
        ) is not None

    def clear(self) -> None:
        """Remove all registered Bodies."""

        self._bodies.clear()

    # =========================================================
    # MANIFEST
    # =========================================================

    @staticmethod
    def _parse_manifest(
        manifest: dict[str, Any],
        client: BodyClient,
    ) -> BodyInfo:
        """Convert a Body response into BodyInfo."""

        if not isinstance(manifest, dict):
            raise BodyRouterError(
                "Body manifest must be a JSON object"
            )

        body_data = manifest.get("body")

        if isinstance(body_data, dict):
            data = body_data
        else:
            data = manifest

        body_id = str(
            data.get("body_id") or ""
        ).strip()

        if not body_id:
            raise BodyRouterError(
                "Body manifest is missing body_id"
            )

        name = str(
            data.get("name") or body_id
        )

        protocol_version = str(
            data.get("protocol_version") or ""
        )

        version = str(
            data.get("version") or ""
        )

        raw_capabilities = data.get(
            "capabilities",
            [],
        )

        if not isinstance(raw_capabilities, list):
            raise BodyRouterError(
                "Body capabilities must be a list"
            )

        capabilities = {
            str(capability).strip()
            for capability in raw_capabilities
            if str(capability).strip()
        }

        return BodyInfo(
            body_id=body_id,
            name=name,
            protocol_version=protocol_version,
            version=version,
            capabilities=capabilities,
            client=client,
        )

    # =========================================================
    # DISCOVERY
    # =========================================================

    def list_bodies(self) -> list[BodyInfo]:
        """Return all registered Bodies."""

        return list(
            self._bodies.values()
        )

    def get_body(
        self,
        body_id: str,
    ) -> BodyInfo | None:
        """Return a registered Body by ID."""

        return self._bodies.get(body_id)

    def capabilities(
        self,
        body_id: str | None = None,
    ) -> dict[str, Any]:
        """Return router-visible capability information."""

        if body_id is not None:

            body = self.get_body(body_id)

            if body is None:
                raise BodyRouterError(
                    f"Unknown Body: {body_id}"
                )

            return body.to_dict()

        return {
            "bodies": [
                body.to_dict()
                for body in self.list_bodies()
            ]
        }

    # =========================================================
    # ROUTING
    # =========================================================

    def find_body(
        self,
        operation: str,
    ) -> BodyInfo:
        """
        Find a Body that advertises the requested operation.

        Selection is deterministic using registration order.
        """

        operation = str(
            operation
        ).strip()

        if not operation:
            raise BodyRouterError(
                "Operation name cannot be empty"
            )

        for body in self._bodies.values():

            if body.supports(operation):
                return body

        raise NoBodyAvailableError(
            f"No registered Body supports operation "
            f"'{operation}'"
        )

    def route(
        self,
        operation: Operation | dict[str, Any],
    ) -> BodyInfo:
        """
        Select a compatible Body for a Core Operation.
        """

        if isinstance(
            operation,
            Operation,
        ):

            operation_name = operation.operation

        elif isinstance(
            operation,
            dict,
        ):

            operation_name = operation.get(
                "operation",
                "",
            )

        else:

            raise TypeError(
                "route() requires Core Operation or dict"
            )

        return self.find_body(
            operation_name
        )

    # =========================================================
    # EXECUTION
    # =========================================================

    def execute(
        self,
        operation: Operation | dict[str, Any],
        *,
        body_id: str | None = None,
        request_id: str | None = None,
        task_id: str | None = None,
        approval_scope: str = "none",
    ) -> dict[str, Any]:
        """
        Route and execute an already-planned operation.

        If body_id is provided, that Body must support the
        requested operation.

        Otherwise the router automatically selects a compatible Body.
        """

        if isinstance(
            operation,
            Operation,
        ):

            operation_name = operation.operation

        elif isinstance(
            operation,
            dict,
        ):

            operation_name = str(
                operation.get(
                    "operation",
                    "",
                )
            ).strip()

        else:

            raise TypeError(
                "execute() requires Core Operation or dict"
            )

        # -----------------------------------------------------
        # Explicit Body selection
        # -----------------------------------------------------

        if body_id is not None:

            body = self.get_body(
                body_id
            )

            if body is None:
                raise BodyRouterError(
                    f"Unknown Body: {body_id}"
                )

            if not body.supports(
                operation_name
            ):
                raise NoBodyAvailableError(
                    f"Body '{body_id}' does not support "
                    f"operation '{operation_name}'"
                )

        # -----------------------------------------------------
        # Automatic Body selection
        # -----------------------------------------------------

        else:

            body = self.find_body(
                operation_name
            )

        # -----------------------------------------------------
        # Send operation through existing BodyClient
        # -----------------------------------------------------

        return body.client.execute(
            operation,
            request_id=request_id,
            task_id=task_id,
            approval_scope=approval_scope,
        )