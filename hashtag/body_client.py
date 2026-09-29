"""
Hashtag Core -> Body transport client.

V1.5

This module bridges the existing Hashtag Core Operation contract
to the Hashtag Executor Body protocol.

Core remains responsible for:
    - understanding
    - planning
    - learning
    - verification
    - recovery

The Body remains responsible for:
    - permissions
    - physical execution
    - returning execution results
"""

from __future__ import annotations

import json
import uuid
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .contracts import Operation


class BodyClientError(RuntimeError):
    """Raised when communication with a Body fails."""


class BodyClient:
    """
    HTTP client used by Hashtag Core to communicate with
    a Hashtag Body.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        url = f"{self.base_url}{path}"

        headers = {
            "Accept": "application/json",
        }

        body = None

        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(
            url,
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout,
            ) as response:

                raw = response.read().decode("utf-8")

        except HTTPError as exc:

            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)

            raise BodyClientError(
                f"Body HTTP {exc.code}: {detail}"
            ) from exc

        except URLError as exc:

            raise BodyClientError(
                f"Could not connect to Body at {url}: {exc.reason}"
            ) from exc

        except TimeoutError as exc:

            raise BodyClientError(
                f"Timed out contacting Body at {url}"
            ) from exc

        try:
            result = json.loads(raw)

        except json.JSONDecodeError as exc:

            raise BodyClientError(
                f"Body returned invalid JSON from {url}"
            ) from exc

        if not isinstance(result, dict):

            raise BodyClientError(
                f"Body returned unexpected response type from {url}"
            )

        return result

    # ---------------------------------------------------------
    # BODY DISCOVERY
    # ---------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """Return Body status and manifest information."""

        return self._request(
            "GET",
            "/v1/body/status",
        )

    def capabilities(self) -> dict[str, Any]:
        """Return the Body capability manifest."""

        return self._request(
            "GET",
            "/v1/body/capabilities",
        )

    # ---------------------------------------------------------
    # OPERATION SERIALIZATION
    # ---------------------------------------------------------

    @staticmethod
    def _serialize_operation(
        operation: Operation,
        *,
        request_id: str | None = None,
        task_id: str | None = None,
        approval_scope: str = "none",
    ) -> dict[str, Any]:
        """
        Convert the existing Core Operation into the transport
        protocol expected by the Executor Body.

        Core's Operation contract is intentionally not changed.
        """

        if not isinstance(operation, Operation):
            raise TypeError(
                "operation must be hashtag.contracts.Operation"
            )

        # IMPORTANT:
        # Core Operation uses as_dict(), not to_dict().
        payload = operation.as_dict()

        # Executor Body protocol metadata.
        payload["protocol_version"] = "1.1"

        payload["request_id"] = (
            request_id
            or uuid.uuid4().hex
        )

        payload["task_id"] = task_id

        payload["approval_scope"] = approval_scope

        # The Body is receiving this from Core.
        payload["source"] = "core"

        return payload

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------

    def execute(
        self,
        operation: Operation | dict[str, Any],
        *,
        request_id: str | None = None,
        task_id: str | None = None,
        approval_scope: str = "none",
    ) -> dict[str, Any]:
        """
        Send an operation to the Body.

        A Core Operation is converted into the Body transport
        representation without modifying Core's contract.
        """

        if isinstance(operation, Operation):

            payload = self._serialize_operation(
                operation,
                request_id=request_id,
                task_id=task_id,
                approval_scope=approval_scope,
            )

        elif isinstance(operation, dict):

            payload = dict(operation)

            payload.setdefault(
                "protocol_version",
                "1.1",
            )

            payload.setdefault(
                "request_id",
                request_id or uuid.uuid4().hex,
            )

            payload.setdefault(
                "task_id",
                task_id,
            )

            payload.setdefault(
                "approval_scope",
                approval_scope,
            )

            payload.setdefault(
                "source",
                "core",
            )

        else:

            raise TypeError(
                "execute() requires Core Operation or dict"
            )

        return self._request(
            "POST",
            "/v1/body/execute",
            payload,
        )

    def execute_operation(
        self,
        operation: str,
        arguments: dict[str, Any] | None = None,
        *,
        reason: str = "",
        source: str = "brain",
        provenance: str = "v11",
        preconditions: list[dict[str, Any]] | None = None,
        request_id: str | None = None,
        task_id: str | None = None,
        approval_scope: str = "none",
    ) -> dict[str, Any]:
        """
        Convenience method for explicitly executing a Core
        operation.

        This method does not perform planning.
        """

        core_operation = Operation(
            operation=operation,
            arguments=dict(arguments or {}),
            reason=reason,
            source=source,
            provenance=provenance,
            preconditions=list(
                preconditions or []
            ),
        )

        return self.execute(
            core_operation,
            request_id=request_id,
            task_id=task_id,
            approval_scope=approval_scope,
        )