from __future__ import annotations
from typing import Any, Mapping
from .capability_manifest import CapabilitySpec
from .capability_registry import CapabilityRegistry
from .capability_schema import CapabilityIOContract, IOSchema, SchemaField

class CapabilitySchemaBridgeError(ValueError):
    pass

class CapabilitySchemaBridge:
    VERSION = "2.0-G8-S4"

    def __init__(self, capability_registry: CapabilityRegistry):
        self.capability_registry = capability_registry

    def contract_from_spec(self, spec: CapabilitySpec) -> CapabilityIOContract:
        if not isinstance(spec, CapabilitySpec):
            raise CapabilitySchemaBridgeError("spec must be a CapabilitySpec")
        return CapabilityIOContract(
            capability_id=spec.capability_id,
            input_schema=self._normalize_schema(spec.input_schema),
            output_schema=self._normalize_schema(spec.output_schema),
            consumes=tuple(spec.consumes),
            produces=tuple(spec.produces),
        )

    def get_contract(self, capability_id: str, body_id: str | None = None):
        if body_id is not None:
            specs = self.capability_registry.body_capabilities(body_id)
        else:
            specs = [s for m in self.capability_registry.list_manifests()
                      for s in m.capabilities]
        for spec in specs:
            if spec.capability_id == str(capability_id):
                return self.contract_from_spec(spec)
        return None

    def contracts_for_body(self, body_id: str):
        return [self.contract_from_spec(s)
                for s in self.capability_registry.body_capabilities(body_id)]

    def list_contracts(self):
        return [self.contract_from_spec(s)
                for m in self.capability_registry.list_manifests()
                for s in m.capabilities]

    def validate_input(self, capability_id: str, value: Mapping[str, Any],
                       *, body_id: str | None = None, partial: bool = False):
        contract = self.get_contract(capability_id, body_id)
        if contract is None:
            return [f"unknown capability: {capability_id}"]
        return contract.validate_input(value, partial=partial)

    def validate_output(self, capability_id: str, value: Mapping[str, Any],
                        *, body_id: str | None = None):
        contract = self.get_contract(capability_id, body_id)
        if contract is None:
            return [f"unknown capability: {capability_id}"]
        return contract.validate_output(value)

    def compatible_successors(self, capability_id: str, *, body_id: str | None = None):
        previous = self.get_contract(capability_id, body_id)
        if previous is None:
            return []
        return [c for c in self.list_contracts()
                if c.capability_id != previous.capability_id
                and c.can_follow(previous)]

    @staticmethod
    def _normalize_schema(schema: Mapping[str, Any] | None) -> IOSchema:
        data = dict(schema or {})
        if data.get("type") == "object" or "properties" in data:
            properties = data.get("properties") or {}
            required = set(data.get("required") or [])
            fields = []
            for name, raw in properties.items():
                raw = dict(raw or {})
                fields.append(SchemaField(
                    name=str(name),
                    type=CapabilitySchemaBridge._type_name(raw.get("type", "any")),
                    required=str(name) in required,
                    description=str(raw.get("description", "")),
                    enum=tuple(raw.get("enum") or ()),
                    default=raw.get("default"),
                ))
            return IOSchema(
                fields=fields,
                allow_extra=data.get("additionalProperties") is not False,
                description=str(data.get("description", "")),
            )
        if "fields" in data:
            return IOSchema.from_dict(data)
        return IOSchema(description=str(data.get("description", "")))

    @staticmethod
    def _type_name(value: Any) -> str:
        if isinstance(value, list):
            return str(value[0]) if value else "any"
        return str(value or "any")
