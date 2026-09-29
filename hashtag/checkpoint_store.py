"""V1.8 Gate 6: hardened in-process graph checkpoint storage.

Gate 6 Step 1 keeps the Gate 5 checkpoint model but adds an explicit lifecycle:
    paused -> resuming -> paused
    paused -> resuming -> completed

The store remains intentionally in-process. Persistence across a Core restart is
out of scope for this step.
"""

from __future__ import annotations

import threading
import time
import uuid
from typing import Any, Dict, Optional

from .operation_graph import OperationGraph


class CheckpointError(Exception):
    """Base checkpoint error."""


class CheckpointNotFoundError(CheckpointError):
    """Raised when a checkpoint is missing or expired."""


class CheckpointStateError(CheckpointError):
    """Raised when an invalid checkpoint lifecycle transition is requested."""


class GraphCheckpointStore:
    VERSION = "1.8-G6"
    STATES = {"paused", "resuming", "completed"}

    def __init__(self, ttl_seconds: int = 3600, max_items: int = 100):
        self.ttl_seconds = max(60, int(ttl_seconds))
        self.max_items = max(1, int(max_items))
        self._items: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def _purge(self) -> None:
        now = time.time()
        expired = [
            key
            for key, item in self._items.items()
            if now - float(item.get("created_at", now)) > self.ttl_seconds
        ]
        for key in expired:
            self._items.pop(key, None)

        if len(self._items) <= self.max_items:
            return

        ordered = sorted(
            self._items.items(),
            key=lambda pair: float(pair[1].get("created_at", 0)),
        )
        for key, _ in ordered[: len(self._items) - self.max_items]:
            self._items.pop(key, None)

    def _get_locked(self, checkpoint_id: str) -> Dict[str, Any]:
        key = str(checkpoint_id or "").strip()
        if not key:
            raise CheckpointNotFoundError("Checkpoint ID is required")
        item = self._items.get(key)
        if item is None:
            raise CheckpointNotFoundError(
                f"Checkpoint not found or expired: {key}"
            )
        return item

    def create(
        self,
        *,
        graph: OperationGraph,
        request: str,
        tool: Dict[str, Any],
        body_id: Optional[str],
        approval_scope: str,
        task_id: Optional[str],
        input_text: str,
        context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not isinstance(graph, OperationGraph):
            raise CheckpointError("graph must be an OperationGraph")

        checkpoint_id = "chk_" + uuid.uuid4().hex[:20]
        now = time.time()
        item = {
            "checkpoint_id": checkpoint_id,
            "created_at": now,
            "updated_at": None,
            "status": "paused",
            "graph": graph.as_dict(),
            "request": str(request or ""),
            "tool": dict(tool or {}),
            "body_id": body_id,
            "approval_scope": str(approval_scope or "none"),
            "task_id": task_id,
            "input_text": str(input_text or ""),
            "context": dict(context or {}),
            "metadata": dict(metadata or {}),
        }

        with self._lock:
            self._purge()
            self._items[checkpoint_id] = item
            self._purge()

        return self._public(item)

    def get(self, checkpoint_id: str) -> Dict[str, Any]:
        with self._lock:
            self._purge()
            item = self._get_locked(checkpoint_id)
            return dict(item)

    def graph(self, checkpoint_id: str) -> OperationGraph:
        item = self.get(checkpoint_id)
        return OperationGraph.from_dict(item["graph"])

    def begin_resume(self, checkpoint_id: str) -> Dict[str, Any]:
        """Atomically transition a paused checkpoint into resuming state."""
        with self._lock:
            self._purge()
            item = self._get_locked(checkpoint_id)
            state = str(item.get("status", "paused"))

            if state == "completed":
                raise CheckpointStateError(
                    f"Checkpoint already completed: {checkpoint_id}"
                )
            if state != "paused":
                raise CheckpointStateError(
                    f"Checkpoint cannot begin resume from state '{state}': "
                    f"{checkpoint_id}"
                )

            item["status"] = "resuming"
            item["updated_at"] = time.time()
            return self._public(item)

    def mark_paused(
        self,
        checkpoint_id: str,
        *,
        graph: Optional[OperationGraph] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return a resumed checkpoint to paused after another permission pause."""
        with self._lock:
            self._purge()
            item = self._get_locked(checkpoint_id)
            state = str(item.get("status", "paused"))

            if state not in {"paused", "resuming"}:
                raise CheckpointStateError(
                    f"Checkpoint cannot become paused from state '{state}': "
                    f"{checkpoint_id}"
                )

            if graph is not None:
                if not isinstance(graph, OperationGraph):
                    raise CheckpointError("graph must be an OperationGraph")
                item["graph"] = graph.as_dict()

            item["status"] = "paused"
            item["updated_at"] = time.time()

            if metadata:
                merged = dict(item.get("metadata") or {})
                merged.update(metadata)
                item["metadata"] = merged

            return self._public(item)

    def mark_completed(
        self,
        checkpoint_id: str,
        *,
        graph: Optional[OperationGraph] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Mark a checkpoint permanently completed."""
        with self._lock:
            self._purge()
            item = self._get_locked(checkpoint_id)
            state = str(item.get("status", "paused"))

            if state == "completed":
                # Idempotent completion is safe.
                return self._public(item)

            if state != "resuming":
                raise CheckpointStateError(
                    f"Checkpoint cannot become completed from state '{state}': "
                    f"{checkpoint_id}"
                )

            if graph is not None:
                if not isinstance(graph, OperationGraph):
                    raise CheckpointError("graph must be an OperationGraph")
                item["graph"] = graph.as_dict()

            item["status"] = "completed"
            item["updated_at"] = time.time()

            if metadata:
                merged = dict(item.get("metadata") or {})
                merged.update(metadata)
                item["metadata"] = merged

            return self._public(item)

    def update(
        self,
        checkpoint_id: str,
        *,
        graph: OperationGraph,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update graph state while preserving the checkpoint lifecycle."""
        if not isinstance(graph, OperationGraph):
            raise CheckpointError("graph must be an OperationGraph")

        with self._lock:
            self._purge()
            item = self._get_locked(checkpoint_id)

            if str(item.get("status", "paused")) == "completed":
                raise CheckpointStateError(
                    f"Completed checkpoint cannot be updated: {checkpoint_id}"
                )

            item["graph"] = graph.as_dict()
            item["updated_at"] = time.time()

            if metadata:
                merged = dict(item.get("metadata") or {})
                merged.update(metadata)
                item["metadata"] = merged

            return self._public(item)

    def delete(self, checkpoint_id: str) -> None:
        key = str(checkpoint_id or "").strip()
        with self._lock:
            self._purge()
            if key not in self._items:
                raise CheckpointNotFoundError(
                    f"Checkpoint not found or expired: {key}"
                )
            self._items.pop(key, None)

    def count(self) -> int:
        with self._lock:
            self._purge()
            return len(self._items)

    @staticmethod
    def _public(item: Dict[str, Any]) -> Dict[str, Any]:
        graph = item.get("graph") or {}
        states = {
            node.get("node_id"): node.get("state")
            for node in graph.get("nodes", [])
            if isinstance(node, dict)
        }
        return {
            "checkpoint_id": item.get("checkpoint_id"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "status": item.get("status", "paused"),
            "graph_id": graph.get("graph_id"),
            "states": states,
            "metadata": dict(item.get("metadata") or {}),
        }
