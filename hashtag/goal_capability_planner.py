"""
Hashtag Gate 8 Step 6
Generic capability composition over the existing GoalCapabilityPlanner.

This replacement keeps one planning subsystem. It extends the Gate 8 Step 5
planner so it can reason over capability I/O contracts, external arguments,
and previously-produced fields when selecting a capability chain.

No Body is executed here and no second Brain/planner/executor/memory is
introduced. The resulting OperationGraph remains the existing graph contract.

Key behavior:
- infer broad goal intents
- discover candidate capabilities from the central CapabilityRegistry
- search for a compatible capability sequence
- use I/O contracts plus supplied arguments to determine whether inputs can
  be bound
- emit explicit "$from" argument references for data produced by an earlier
  graph node
- report unresolved required inputs as diagnostics instead of inventing data
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .capability_registry import CapabilityRegistry
from .capability_schema_bridge import CapabilitySchemaBridge
from .capability_schema import CapabilityIOContract
from .contracts import Operation
from .operation_graph import OperationGraph


VERSION = "2.0-G8-S6"


@dataclass(frozen=True)
class CapabilityRequirement:
    capability_id: str
    reason: str = ""
    confidence: float = 1.0
    source: str = "goal_reasoning"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "reason": self.reason,
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass
class GoalPlan:
    goal: str
    requirements: List[CapabilityRequirement] = field(default_factory=list)
    graph: Optional[OperationGraph] = None
    diagnostics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "requirements": [x.as_dict() for x in self.requirements],
            "graph": self.graph.as_dict() if self.graph is not None else None,
            "diagnostics": list(self.diagnostics),
            "metadata": dict(self.metadata),
        }


class GoalCapabilityPlanner:
    """
    Generic capability-to-operation-graph composer.

    Gate 8 Step 6 extends Step 5 by using the registered I/O contracts as
    actual composition constraints. Capability IDs/descriptions/tags provide
    semantic evidence for candidate selection; schemas determine whether a
    candidate can consume the currently available data.

    This is still the existing central planner. It is not a second planning
    runtime.
    """

    VERSION = VERSION

    INTENTS: Dict[str, Tuple[str, ...]] = {
        "read": ("read", "inspect", "open", "load", "view", "analyze", "analyse"),
        "write": ("write", "save", "fix", "correct", "edit", "modify", "update", "change"),
        "execute": ("run", "execute", "test", "check", "compile"),
        "search": ("search", "find", "look up", "lookup"),
        "list": ("list", "show files", "enumerate"),
        "create": ("create", "make", "generate", "build"),
    }

    def __init__(
        self,
        capability_registry: CapabilityRegistry,
        schema_bridge: Optional[CapabilitySchemaBridge] = None,
    ) -> None:
        if capability_registry is None:
            raise ValueError("capability_registry is required")
        self.registry = capability_registry
        self.schemas = schema_bridge or CapabilitySchemaBridge(capability_registry)

    def requirements_for_goal(self, goal: str) -> List[CapabilityRequirement]:
        text = str(goal or "").strip().lower()
        if not text:
            return []

        requirements: List[CapabilityRequirement] = []
        wants_change = self._has_any(text, self.INTENTS["write"])
        wants_run = self._has_any(text, self.INTENTS["execute"])
        wants_read = self._has_any(text, self.INTENTS["read"])

        if wants_change and not wants_read:
            requirements.append(
                CapabilityRequirement(
                    "read",
                    "Inspect existing input before changing it.",
                    confidence=0.95,
                )
            )

        if wants_read:
            requirements.append(
                CapabilityRequirement("read", "The goal requires inspecting or reading input.")
            )

        if wants_change:
            requirements.append(
                CapabilityRequirement("write", "The goal requires producing or changing an artifact.")
            )

        if wants_run:
            requirements.append(
                CapabilityRequirement("execute", "The goal explicitly requires execution or testing.")
            )

        if self._has_any(text, self.INTENTS["search"]):
            requirements.append(
                CapabilityRequirement("search", "The goal requires locating information or files.")
            )

        if self._has_any(text, self.INTENTS["list"]):
            requirements.append(
                CapabilityRequirement("list", "The goal requires enumeration.")
            )

        if self._has_any(text, self.INTENTS["create"]):
            requirements.append(
                CapabilityRequirement("create", "The goal requires creating a new artifact.")
            )

        seen = set()
        result: List[CapabilityRequirement] = []
        for requirement in requirements:
            if requirement.capability_id not in seen:
                seen.add(requirement.capability_id)
                result.append(requirement)
        return result

    def plan(
        self,
        goal: str,
        *,
        arguments: Optional[Mapping[str, Any]] = None,
        body_id: Optional[str] = None,
        graph_id: str = "goal_plan",
    ) -> GoalPlan:
        goal_text = str(goal or "").strip()
        args = dict(arguments or {})
        requirements = self.requirements_for_goal(goal_text)

        if not requirements:
            return GoalPlan(
                goal=goal_text,
                requirements=[],
                graph=None,
                diagnostics=["No capability intent could be inferred from the goal."],
                metadata={"version": self.VERSION},
            )

        candidates: Dict[str, List[str]] = {}
        for req in requirements:
            ranked = self._rank_capabilities(req.capability_id, body_id=body_id)
            candidates[req.capability_id] = ranked

        selected = self._find_composable_path(
            requirements,
            candidates,
            args,
            body_id=body_id,
        )

        diagnostics: List[str] = []
        contract_driven = selected is not None

        if selected is None:
            # Backward-compatible composition path. Existing Gate 8 Step 5
            # fixtures and older capability manifests may not expose complete
            # typed I/O contracts. In that case, preserve the established
            # semantic capability selection instead of making the new schema
            # layer a hard prerequisite for every existing planner call.
            #
            # We still reject a request when a required intent has no
            # capability at all.
            missing = [
                req.capability_id
                for req in requirements
                if not candidates.get(req.capability_id)
            ]
            if missing:
                diagnostics.extend(
                    f"No registered capability satisfies intent: {intent}"
                    for intent in missing
                )
                return GoalPlan(
                    goal=goal_text,
                    requirements=requirements,
                    graph=None,
                    diagnostics=diagnostics,
                    metadata={
                        "version": self.VERSION,
                        "body_id": body_id,
                        "generic_composition": True,
                    },
                )

            selected = []
            for req in requirements:
                capability_id = self._select_capability(
                    req.capability_id,
                    body_id=body_id,
                )
                if capability_id is None:
                    diagnostics.append(
                        f"No registered capability satisfies intent: {req.capability_id}"
                    )
                    return GoalPlan(
                        goal=goal_text,
                        requirements=requirements,
                        graph=None,
                        diagnostics=diagnostics,
                        metadata={
                            "version": self.VERSION,
                            "body_id": body_id,
                            "generic_composition": True,
                        },
                    )
                # Even in the backward-compatible semantic path, do not
                # construct an operation that is known to be missing a
                # required input. Complete contracts remain authoritative for
                # this safety check; only composition itself falls back.
                contract = self.schemas.get_contract(capability_id, body_id)
                if contract is not None:
                    missing_inputs = [
                        field.name
                        for field in contract.input_schema.fields
                        if field.required and field.name not in args
                    ]
                    # A single-step request has no earlier node from which a
                    # missing value can be supplied. Reject it rather than
                    # inventing the value. For a multi-step legacy plan,
                    # preserve Step 5's established semantic composition
                    # behavior; its existing graph/runtime may supply the
                    # intermediate value through the normal execution path.
                    if missing_inputs and len(requirements) == 1:
                        diagnostics.append(
                            f"Required inputs missing for {capability_id}: "
                            + ", ".join(missing_inputs)
                        )
                        return GoalPlan(
                            goal=goal_text,
                            requirements=requirements,
                            graph=None,
                            diagnostics=diagnostics,
                            metadata={
                                "version": self.VERSION,
                                "body_id": body_id,
                                "generic_composition": True,
                                "contract_driven": False,
                            },
                        )

                selected.append((req.capability_id, capability_id))
            diagnostics.append(
                "Contract-driven composition was unavailable for this capability "
                "set; used the existing semantic composition path."
            )

        operations: List[Operation] = []
        dependencies: List[List[str]] = []
        previous_node: Optional[str] = None
        available_fields = set(args.keys())
        bindings: List[Dict[str, Any]] = []
        unresolved: List[str] = []

        for index, (intent, capability_id) in enumerate(selected, start=1):
            contract = self.schemas.get_contract(capability_id, body_id)
            node_args = dict(args)
            node_bindings: Dict[str, Any] = {}

            if contract is not None and contract_driven:
                for field in contract.input_schema.fields:
                    if field.name in node_args:
                        continue
                    source = self._find_source_field(
                        field.name,
                        previous_output_fields=self._previous_output_fields(
                            selected, index - 1, body_id
                        ),
                    )
                    if source is not None:
                        node_args[field.name] = {
                            "$from": source[0],
                            "field": source[1],
                        }
                        node_bindings[field.name] = {
                            "$from": source[0],
                            "field": source[1],
                        }
                    elif field.required:
                        unresolved.append(
                            f"{capability_id}.{field.name}"
                        )

            operation = Operation(
                operation=capability_id,
                arguments=node_args,
                reason=f"Goal intent '{intent}' selected capability '{capability_id}'.",
                source="brain",
                provenance="v11",
                preconditions=[],
            )
            operations.append(operation)
            dependencies.append([f"op_{index - 1}"] if previous_node else [])
            previous_node = f"op_{index}"

            if contract is not None:
                available_fields.update(
                    field.name for field in contract.output_schema.fields
                )
            bindings.append(
                {
                    "node_id": f"op_{index}",
                    "capability_id": capability_id,
                    "arguments": node_bindings,
                }
            )

        if unresolved:
            diagnostics.append(
                "Unresolved required inputs: " + ", ".join(unresolved)
            )

        graph = OperationGraph.from_operations(
            operations,
            graph_id=graph_id,
            dependencies=dependencies,
            metadata={
                "planner": self.VERSION,
                "goal": goal_text,
                "body_id": body_id,
                "generic_composition": True,
                "contract_driven": True,
                "requirements": [r.as_dict() for r in requirements],
                "bindings": bindings,
            },
        )

        return GoalPlan(
            goal=goal_text,
            requirements=requirements,
            graph=graph,
            diagnostics=diagnostics,
            metadata={
                "version": self.VERSION,
                "body_id": body_id,
                "selected_capabilities": [cap for _, cap in selected],
                "contract_driven": contract_driven,
                "bindings": bindings,
            },
        )

    def _find_composable_path(
        self,
        requirements: Sequence[CapabilityRequirement],
        candidates: Mapping[str, Sequence[str]],
        arguments: Mapping[str, Any],
        *,
        body_id: Optional[str],
    ) -> Optional[List[Tuple[str, str]]]:
        """
        Bounded backtracking over semantic candidates.

        The search is intentionally small and deterministic. It is not a
        second planner; it is the composition phase of GoalCapabilityPlanner.
        """
        limit = 8

        def search(
            index: int,
            chosen: List[Tuple[str, str]],
            available_fields: set[str],
        ) -> Optional[List[Tuple[str, str]]]:
            if index >= len(requirements):
                return list(chosen)

            req = requirements[index]
            ranked = candidates.get(req.capability_id, ())
            for capability_id in ranked[:limit]:
                if capability_id in {cap for _, cap in chosen}:
                    continue

                contract = self.schemas.get_contract(capability_id, body_id)
                if contract is None:
                    continue

                if not self._inputs_bindable(
                    contract,
                    available_fields,
                    arguments,
                    chosen,
                    body_id,
                ):
                    continue

                output_fields = {
                    field.name for field in contract.output_schema.fields
                }
                next_fields = set(available_fields)
                next_fields.update(output_fields)

                chosen.append((req.capability_id, capability_id))
                result = search(index + 1, chosen, next_fields)
                chosen.pop()

                if result is not None:
                    return result

            return None

        return search(0, [], set(arguments.keys()))

    def _inputs_bindable(
        self,
        contract: CapabilityIOContract,
        available_fields: set[str],
        arguments: Mapping[str, Any],
        chosen: Sequence[Tuple[str, str]],
        body_id: Optional[str],
    ) -> bool:
        for field in contract.input_schema.fields:
            if not field.required:
                continue
            if field.name in arguments:
                continue
            if field.name in available_fields:
                continue
            if self._find_source_field(
                field.name,
                previous_output_fields=self._previous_output_fields(
                    chosen, len(chosen), body_id
                ),
            ) is not None:
                continue
            return False
        return True

    def _previous_output_fields(
        self,
        selected: Sequence[Tuple[str, str]],
        count: int,
        body_id: Optional[str],
    ) -> List[Tuple[str, str, str]]:
        result: List[Tuple[str, str, str]] = []
        for index, (_, capability_id) in enumerate(selected[:count], start=1):
            contract = self.schemas.get_contract(capability_id, body_id)
            if contract is None:
                continue
            for field in contract.output_schema.fields:
                result.append((f"op_{index}", field.name, capability_id))
        return result

    @staticmethod
    def _find_source_field(
        required_name: str,
        *,
        previous_output_fields: Sequence[Tuple[str, str, str]],
    ) -> Optional[Tuple[str, str]]:
        # Exact field names are authoritative for safe automatic binding.
        for node_id, field_name, _ in previous_output_fields:
            if field_name == required_name:
                return node_id, field_name
        return None

    def _rank_capabilities(
        self,
        intent: str,
        *,
        body_id: Optional[str],
    ) -> List[str]:
        specs = (
            self.registry.body_capabilities(body_id)
            if body_id is not None
            else [
                spec
                for manifest in self.registry.list_manifests()
                for spec in manifest.capabilities
            ]
        )
        scored: List[Tuple[float, str]] = []

        for spec in specs:
            capability_id = str(spec.capability_id)
            text = " ".join(
                [
                    capability_id,
                    str(spec.description),
                    " ".join(spec.tags),
                    " ".join(spec.consumes),
                    " ".join(spec.produces),
                ]
            ).lower()

            score = 0.0
            for word in self.INTENTS.get(intent, (intent,)):
                if word in capability_id.lower():
                    score += 6.0
                if word in text:
                    score += 2.0

            if intent == "read" and ".read" in capability_id:
                score += 4.0
            elif intent == "write" and ".write" in capability_id:
                score += 4.0
            elif intent == "execute" and (
                ".execute" in capability_id or ".run" in capability_id
            ):
                score += 4.0
            elif intent == "search" and ".search" in capability_id:
                score += 4.0
            elif intent == "list" and ".list" in capability_id:
                score += 4.0
            elif intent == "create" and ".create" in capability_id:
                score += 4.0

            if score > 0:
                scored.append((score, capability_id))

        scored.sort(key=lambda item: (-item[0], item[1]))
        return [capability_id for _, capability_id in scored]

    def _select_capability(self, intent: str, *, body_id: Optional[str]) -> Optional[str]:
        ranked = self._rank_capabilities(intent, body_id=body_id)
        return ranked[0] if ranked else None

    @staticmethod
    def _has_any(text: str, terms: Iterable[str]) -> bool:
        return any(term in text for term in terms)


__all__ = [
    "CapabilityRequirement",
    "GoalPlan",
    "GoalCapabilityPlanner",
    "VERSION",
]
