"""Hashtag Gate 8 Step 1: capability manifest contract.

This module describes what a Body can do without teaching the Brain every
high-level task. It is intentionally declarative: it contains capability
metadata, input/output contracts, safety metadata, and optional relationships.

It does not execute anything and does not contain planning logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


VERSION = "2.0-G8-S1"


@dataclass
class CapabilitySpec:
    """Declarative description of one Body capability."""

    capability_id: str
    description: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)

    # Human/Brain-readable semantic information.
    tags: List[str] = field(default_factory=list)

    # Execution/safety information. These are metadata only; the Body still
    # enforces its own permissions.
    side_effects: List[str] = field(default_factory=list)
    risk_level: str = "low"

    # Optional composition hints. They describe data flow, not a hard-coded
    # workflow.
    consumes: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)

    # Optional Body-specific metadata.
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.capability_id = str(self.capability_id or "").strip()
        if not self.capability_id:
            raise ValueError("capability_id is required")

        self.description = str(self.description or "")
        self.risk_level = str(self.risk_level or "low").strip().lower()

        if self.risk_level not in {"low", "medium", "high", "critical"}:
            raise ValueError(
                "risk_level must be one of: low, medium, high, critical"
            )

        self.tags = _clean_strings(self.tags)
        self.side_effects = _clean_strings(self.side_effects)
        self.consumes = _clean_strings(self.consumes)
        self.produces = _clean_strings(self.produces)

    @property
    def id(self) -> str:
        """Compatibility alias matching the existing Capability contract."""
        return self.capability_id

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.capability_id,
            "capability_id": self.capability_id,
            "description": self.description,
            "input_schema": dict(self.input_schema),
            "output_schema": dict(self.output_schema),
            "tags": list(self.tags),
            "side_effects": list(self.side_effects),
            "risk_level": self.risk_level,
            "consumes": list(self.consumes),
            "produces": list(self.produces),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CapabilitySpec":
        if not isinstance(data, dict):
            raise TypeError("capability specification must be a dictionary")

        capability_id = data.get("capability_id") or data.get("id")
        return cls(
            capability_id=capability_id,
            description=data.get("description", ""),
            input_schema=data.get("input_schema") or {},
            output_schema=data.get("output_schema") or {},
            tags=data.get("tags") or [],
            side_effects=data.get("side_effects") or [],
            risk_level=data.get("risk_level", "low"),
            consumes=data.get("consumes") or [],
            produces=data.get("produces") or [],
            metadata=data.get("metadata") or {},
        )


@dataclass
class CapabilityManifest:
    """Declarative capability manifest published by a Body."""

    body_id: str
    name: str
    version: str
    protocol_version: str
    capabilities: List[CapabilitySpec] = field(default_factory=list)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    VERSION = VERSION

    def __post_init__(self) -> None:
        self.body_id = str(self.body_id or "").strip()
        self.name = str(self.name or "").strip()
        self.version = str(self.version or "").strip()
        self.protocol_version = str(self.protocol_version or "").strip()

        if not self.body_id:
            raise ValueError("body_id is required")
        if not self.name:
            raise ValueError("name is required")
        if not self.version:
            raise ValueError("version is required")
        if not self.protocol_version:
            raise ValueError("protocol_version is required")

        normalized: List[CapabilitySpec] = []
        seen = set()

        for capability in self.capabilities:
            item = (
                capability
                if isinstance(capability, CapabilitySpec)
                else CapabilitySpec.from_dict(capability)
            )
            if item.capability_id in seen:
                raise ValueError(
                    f"duplicate capability in manifest: {item.capability_id}"
                )
            seen.add(item.capability_id)
            normalized.append(item)

        self.capabilities = normalized

    def has_capability(self, capability_id: str) -> bool:
        return any(
            item.capability_id == str(capability_id)
            for item in self.capabilities
        )

    def get_capability(self, capability_id: str) -> Optional[CapabilitySpec]:
        target = str(capability_id)
        for item in self.capabilities:
            if item.capability_id == target:
                return item
        return None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.VERSION,
            "body_id": self.body_id,
            "name": self.name,
            "version": self.version,
            "protocol_version": self.protocol_version,
            "description": self.description,
            "capabilities": [item.as_dict() for item in self.capabilities],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CapabilityManifest":
        if not isinstance(data, dict):
            raise TypeError("capability manifest must be a dictionary")

        return cls(
            body_id=data.get("body_id") or data.get("id"),
            name=data.get("name", ""),
            version=data.get("version", ""),
            protocol_version=data.get("protocol_version", ""),
            description=data.get("description", ""),
            capabilities=data.get("capabilities") or [],
            metadata=data.get("metadata") or {},
        )


def _clean_strings(values: Any) -> List[str]:
    if values is None:
        return []

    if isinstance(values, str):
        values = [values]

    result: List[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in result:
            result.append(text)
    return result
