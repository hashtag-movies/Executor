"""Hashtag Gate 8 Step 1: central capability registry.

The registry is deliberately separate from execution and planning:
Bodies publish manifests, Core indexes them, and later planning stages query
this index. It does not decide how to accomplish a goal.

This is a capability index, not a second Brain or memory system.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, Iterable, List, Optional

from .capability_manifest import CapabilityManifest, CapabilitySpec


VERSION = "2.0-G8-S1"


class CapabilityRegistryError(ValueError):
    """Base error for capability registry operations."""


class CapabilityRegistry:
    """Thread-safe index of capabilities published by connected Bodies."""

    VERSION = VERSION

    def __init__(self) -> None:
        self._manifests: Dict[str, CapabilityManifest] = {}
        self._last_seen: Dict[str, float] = {}
        self._lock = threading.RLock()

    def register(
        self,
        manifest: CapabilityManifest | Dict[str, Any],
    ) -> CapabilityManifest:
        if isinstance(manifest, dict):
            manifest = CapabilityManifest.from_dict(manifest)

        if not isinstance(manifest, CapabilityManifest):
            raise CapabilityRegistryError(
                "manifest must be a CapabilityManifest or dictionary"
            )

        with self._lock:
            self._manifests[manifest.body_id] = manifest
            self._last_seen[manifest.body_id] = time.time()

        return manifest

    def unregister(self, body_id: str) -> bool:
        target = str(body_id or "").strip()
        with self._lock:
            existed = target in self._manifests
            self._manifests.pop(target, None)
            self._last_seen.pop(target, None)
            return existed

    def heartbeat(self, body_id: str) -> bool:
        target = str(body_id or "").strip()
        with self._lock:
            if target not in self._manifests:
                return False
            self._last_seen[target] = time.time()
            return True

    def get(self, body_id: str) -> Optional[CapabilityManifest]:
        with self._lock:
            return self._manifests.get(str(body_id))

    def list_manifests(self) -> List[CapabilityManifest]:
        with self._lock:
            return list(self._manifests.values())

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """Return capability records annotated with their Body."""
        result: List[Dict[str, Any]] = []

        with self._lock:
            for manifest in self._manifests.values():
                for capability in manifest.capabilities:
                    item = capability.as_dict()
                    item["body_id"] = manifest.body_id
                    item["body_name"] = manifest.name
                    item["body_version"] = manifest.version
                    item["protocol_version"] = manifest.protocol_version
                    result.append(item)

        return result

    def find(
        self,
        capability_id: str,
    ) -> List[Dict[str, Any]]:
        """Find every Body that advertises a capability."""
        target = str(capability_id or "").strip()
        if not target:
            return []

        return [
            item
            for item in self.list_capabilities()
            if item["capability_id"] == target
        ]

    def body_capabilities(self, body_id: str) -> List[CapabilitySpec]:
        manifest = self.get(body_id)
        return list(manifest.capabilities) if manifest else []

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Simple metadata search for later Brain matching.

        This is deliberately not a planner. It only ranks manifest records
        against textual terms in names, descriptions, IDs, and tags.
        """
        terms = [
            term
            for term in str(query or "").lower().split()
            if len(term) > 1
        ]

        records = self.list_capabilities()
        scored = []

        for record in records:
            haystack = " ".join(
                [
                    record.get("capability_id", ""),
                    record.get("description", ""),
                    " ".join(record.get("tags", [])),
                    " ".join(record.get("consumes", [])),
                    " ".join(record.get("produces", [])),
                    record.get("body_name", ""),
                ]
            ).lower()

            score = sum(term in haystack for term in terms)
            scored.append((score, record))

        scored.sort(
            key=lambda item: (
                item[0],
                str(item[1].get("capability_id", "")),
                str(item[1].get("body_id", "")),
            ),
            reverse=True,
        )

        return [record for score, record in scored if score > 0]

    def public_list(self) -> List[Dict[str, Any]]:
        now = time.time()
        result = []

        for manifest in self.list_manifests():
            result.append(
                {
                    **manifest.as_dict(),
                    "last_seen": self._last_seen.get(manifest.body_id),
                    "age_seconds": (
                        max(0.0, now - self._last_seen[manifest.body_id])
                        if manifest.body_id in self._last_seen
                        else None
                    ),
                }
            )

        return result

    def clear(self) -> None:
        with self._lock:
            self._manifests.clear()
            self._last_seen.clear()
