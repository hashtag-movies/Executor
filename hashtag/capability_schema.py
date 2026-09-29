from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping
import copy

class SchemaError(ValueError):
    pass

@dataclass(frozen=True)
class SchemaField:
    name: str
    type: str = "any"
    required: bool = False
    description: str = ""
    enum: tuple[Any, ...] = ()
    default: Any = None

    def __post_init__(self):
        if not self.name.strip() or not self.type.strip():
            raise SchemaError("field name and type are required")

    def as_dict(self):
        result = {"name": self.name, "type": self.type, "required": self.required,
                  "description": self.description}
        if self.enum:
            result["enum"] = list(self.enum)
        if self.default is not None:
            result["default"] = copy.deepcopy(self.default)
        return result

    @classmethod
    def from_dict(cls, data):
        return cls(str(data["name"]), str(data.get("type", "any")),
                   bool(data.get("required", False)), str(data.get("description", "")),
                   tuple(data.get("enum", ())), copy.deepcopy(data.get("default")))

@dataclass
class IOSchema:
    fields: list[SchemaField] = field(default_factory=list)
    allow_extra: bool = True
    description: str = ""

    def __post_init__(self):
        names = [f.name for f in self.fields]
        if len(names) != len(set(names)):
            raise SchemaError("duplicate field names are not allowed")

    def field(self, name):
        return next((f for f in self.fields if f.name == name), None)

    def validate(self, value: Mapping[str, Any], *, partial=False):
        if not isinstance(value, Mapping):
            return ["value must be an object"]
        errors = []
        known = {f.name for f in self.fields}
        if not self.allow_extra:
            errors.extend(f"unexpected field: {k}" for k in value if k not in known)
        for f in self.fields:
            if f.required and f.name not in value and not partial:
                errors.append(f"missing required field: {f.name}")
                continue
            if f.name not in value:
                continue
            if not _matches(value[f.name], f.type):
                errors.append(f"field {f.name!r} expected {f.type}, got {type(value[f.name]).__name__}")
            if f.enum and value[f.name] not in f.enum:
                errors.append(f"field {f.name!r} must be one of {list(f.enum)!r}")
        return errors

    def is_compatible_with(self, produced):
        for needed in self.fields:
            if not needed.required:
                continue
            available = produced.field(needed.name)
            if available is None or not _compatible(available.type, needed.type):
                return False
        return True

    def as_dict(self):
        return {"fields": [f.as_dict() for f in self.fields],
                "allow_extra": self.allow_extra, "description": self.description}

    @classmethod
    def from_dict(cls, data):
        return cls([SchemaField.from_dict(x) for x in data.get("fields", [])],
                   bool(data.get("allow_extra", True)), str(data.get("description", "")))

@dataclass(frozen=True)
class CapabilityIOContract:
    capability_id: str
    input_schema: IOSchema
    output_schema: IOSchema
    consumes: tuple[str, ...] = ()
    produces: tuple[str, ...] = ()

    def validate_input(self, value, *, partial=False):
        return self.input_schema.validate(value, partial=partial)

    def validate_output(self, value):
        return self.output_schema.validate(value)

    def can_follow(self, previous):
        return self.input_schema.is_compatible_with(previous.output_schema)

    def as_dict(self):
        return {"capability_id": self.capability_id, "input_schema": self.input_schema.as_dict(),
                "output_schema": self.output_schema.as_dict(), "consumes": list(self.consumes),
                "produces": list(self.produces)}

    @classmethod
    def from_dict(cls, data):
        return cls(str(data["capability_id"]), IOSchema.from_dict(data.get("input_schema", {})),
                   IOSchema.from_dict(data.get("output_schema", {})),
                   tuple(data.get("consumes", ())), tuple(data.get("produces", ())))

def _matches(value, type_name):
    if type_name == "any":
        return True
    if type_name == "object":
        return isinstance(value, Mapping)
    if type_name in ("string", "str"):
        return isinstance(value, str)
    if type_name in ("integer", "int"):
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name in ("number", "float"):
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_name in ("boolean", "bool"):
        return isinstance(value, bool)
    if type_name == "array":
        return isinstance(value, (list, tuple))
    if type_name == "null":
        return value is None
    return True

def _compatible(produced, required):
    aliases = {"str": "string", "int": "integer", "float": "number", "bool": "boolean"}
    produced, required = aliases.get(produced, produced), aliases.get(required, required)
    return produced == required or produced == "any" or required == "any" or (produced == "integer" and required == "number")
