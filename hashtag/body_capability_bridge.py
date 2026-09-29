"""Gate 8 Step 2: synchronize BodyRouter registration with capability metadata."""
from __future__ import annotations
from typing import Any, Dict
from .body_router import BodyRouter
from .capability_manifest import CapabilityManifest
from .capability_registry import CapabilityRegistry

VERSION = "2.0-G8-S2"

class BodyCapabilityBridge:
    VERSION = VERSION

    def __init__(self, body_router: BodyRouter, capability_registry: CapabilityRegistry):
        self.body_router = body_router
        self.capability_registry = capability_registry

    def register(self, body: Any, manifest: CapabilityManifest | Dict[str, Any]) -> Any:
        registered = self.body_router.register(body)
        self.capability_registry.register(manifest)
        return registered

    def unregister(self, body_id: str) -> bool:
        removed = self.capability_registry.unregister(body_id)
        fn = getattr(self.body_router, "unregister", None)
        if callable(fn):
            result = fn(body_id)
            return removed or bool(result if result is not None else True)
        return removed

    def heartbeat(self, body_id: str) -> bool:
        return self.capability_registry.heartbeat(body_id)

    def capabilities_for_body(self, body_id: str):
        return self.capability_registry.body_capabilities(body_id)

    def public_list(self):
        return self.capability_registry.public_list()
