import re
from typing import Any, Dict, Iterable, List


class HashtagOperationRuntime:
    """
    Shared deterministic operation runtime.

    Authoritative implementation of V10 operation semantics used by
    simulation and Body execution.

    The runtime does not perform planning, learning, permissions, or
    natural-language interpretation.
    """

    VERSION = "1.1"

    # Sorting requires the complete input and therefore cannot be performed
    # by the bounded streaming executor.
    STREAM_UNSUPPORTED = {
        "format.sort_lines",
    }

    @staticmethod
    def _operation_parts(operation: Any):
        if hasattr(operation, "operation"):
            capability = operation.operation
            arguments = dict(operation.arguments or {})

        elif hasattr(operation, "as_dict"):
            raw = operation.as_dict()
            capability = raw.get("capability") or raw.get("operation")
            arguments = dict(raw.get("arguments") or {})

        elif isinstance(operation, dict):
            capability = operation.get("capability") or operation.get("operation")
            arguments = dict(operation.get("arguments") or {})

        else:
            raise TypeError(
                f"Unsupported operation type: {type(operation)!r}"
            )

        return capability, arguments

    @classmethod
    def apply_one(cls, lines: List[str], operation: Any) -> List[str]:
        capability, x = cls._operation_parts(operation)

        if capability == "text.remove_digits":
            return [
                re.sub(r"[0-9]", "", value)
                for value in lines
            ]

        if capability == "text.remove_letters":
            return [
                re.sub(r"[A-Za-z]", "", value)
                for value in lines
            ]

        if capability == "text.replace":
            old = str(x.get("old", ""))
            new = str(x.get("new", ""))

            return [
                value.replace(old, new)
                for value in lines
            ]

        if capability == "text.regex_replace":
            try:
                flags = (
                    re.I
                    if "i" in str(x.get("flags", ""))
                    else 0
                )

                regex = re.compile(
                    str(x.get("pattern", "")),
                    flags,
                )

                return [
                    regex.sub(
                        str(x.get("to", "")),
                        value,
                    )
                    for value in lines
                ]

            except re.error:
                # Preserve existing Sandbox behavior.
                return lines

        if capability == "filter.keep_contains":
            values = [
                str(v).lower()
                for v in x.get("values", [])
            ]

            return [
                value
                for value in lines
                if any(
                    q in value.lower()
                    for q in values
                )
            ]

        if capability == "filter.remove_contains":
            values = [
                str(v).lower()
                for v in x.get("values", [])
            ]

            return [
                value
                for value in lines
                if not any(
                    q in value.lower()
                    for q in values
                )
            ]

        if capability == "format.remove_duplicates":
            return list(dict.fromkeys(lines))

        if capability == "format.remove_number_only":
            return [
                value
                for value in lines
                if not re.fullmatch(
                    r"\s*\d+(?:\.\d+)?\s*",
                    value,
                )
            ]

        if capability == "format.lowercase":
            return [
                value.lower()
                for value in lines
            ]

        if capability == "format.uppercase":
            return [
                value.upper()
                for value in lines
            ]

        if capability == "format.normalize_spaces":
            return [
                re.sub(r"\s+", " ", value).strip()
                for value in lines
            ]

        if capability == "format.trim":
            return [
                value.strip()
                for value in lines
            ]

        if capability == "format.keep_before":
            separator = str(
                x.get("separator", "")
            )

            if not separator:
                return lines

            return [
                value.split(separator, 1)[0].rstrip()
                if separator in value
                else value
                for value in lines
            ]

        if capability == "format.keep_after":
            separator = str(
                x.get("separator", "")
            )

            if not separator:
                return lines

            return [
                value.split(separator, 1)[1].lstrip()
                if separator in value
                else value
                for value in lines
            ]

        if capability == "format.sort_lines":
            reverse = x.get("order") == "desc"

            return sorted(
                lines,
                key=lambda value: value.casefold(),
                reverse=reverse,
            )

        if capability == "format.pick_fields":
            input_delimiter = str(
                x.get(
                    "inputDelimiter",
                    x.get("delimiter", ":"),
                )
            )

            output_delimiter = str(
                x.get(
                    "delimiter",
                    input_delimiter,
                )
            )

            fields = [
                int(index)
                for index in x.get("fields", [])
            ]

            return [
                output_delimiter.join(
                    parts[index - 1]
                    if 0 < index <= len(parts)
                    else ""
                    for index in fields
                )
                for parts in (
                    line.split(input_delimiter)
                    for line in lines
                )
            ]

        if capability == "format.join_blocks":
            size = max(
                1,
                int(x.get("size", 1)),
            )

            delimiter = str(
                x.get("delimiter", ":")
            )

            return [
                delimiter.join(
                    lines[i:i + size]
                )
                for i in range(
                    0,
                    len(lines),
                    size,
                )
            ]

        # Preserve existing behavior for unknown operations.
        return lines

    @classmethod
    def apply(
        cls,
        text: str,
        operations: Iterable[Any],
    ) -> str:
        lines = (text or "").splitlines()

        for operation in operations or []:
            lines = cls.apply_one(
                lines,
                operation,
            )

        return "\n".join(lines)

    @classmethod
    def apply_stream_lines(
        cls,
        lines: Iterable[str],
        operations: Iterable[Any],
    ) -> List[str]:
        """
        Apply operations to one independent chunk.

        This method is intentionally stateless. It is useful for callers
        that already manage operation state externally.

        create_stream() below is the authoritative stateful streaming path.
        """

        operations = list(operations or [])

        for operation in operations:
            capability, _ = cls._operation_parts(operation)

            if capability in cls.STREAM_UNSUPPORTED:
                raise ValueError(
                    f"Operation {capability!r} is not streamable"
                )

        result = list(lines)

        for operation in operations:
            result = cls.apply_one(
                result,
                operation,
            )

        return result

    @classmethod
    def create_stream(
        cls,
        operations: Iterable[Any],
        chunk_size: int = 10000,
    ):
        """
        Create a bounded streaming processor.

        Streaming operations retain only the state required to preserve
        their semantics across chunk boundaries.

        Current stateful operations:

        - format.remove_duplicates
        - format.join_blocks

        format.sort_lines remains explicitly non-streamable.
        """

        if chunk_size < 1:
            raise ValueError(
                "chunk_size must be >= 1"
            )

        operations = list(
            operations or []
        )

        parsed = []

        for operation in operations:
            capability, arguments = cls._operation_parts(
                operation
            )

            if capability in cls.STREAM_UNSUPPORTED:
                raise ValueError(
                    f"Operation {capability!r} is not streamable"
                )

            state = {}

            if capability == "format.remove_duplicates":
                state["seen"] = set()

            elif capability == "format.join_blocks":
                state["pending"] = []
                state["size"] = max(
                    1,
                    int(arguments.get("size", 1)),
                )
                state["delimiter"] = str(
                    arguments.get(
                        "delimiter",
                        ":",
                    )
                )

            parsed.append(
                (
                    operation,
                    capability,
                    arguments,
                    state,
                )
            )

        def apply_stream_operation(
            values,
            capability,
            arguments,
            state,
        ):
            values = list(values)

            if capability == "format.remove_duplicates":
                output = []

                for value in values:
                    if value not in state["seen"]:
                        state["seen"].add(value)
                        output.append(value)

                return output

            if capability == "format.join_blocks":
                pending = state["pending"]
                pending.extend(values)

                size = state["size"]
                delimiter = state["delimiter"]

                output = []

                while len(pending) >= size:
                    group = pending[:size]
                    del pending[:size]

                    output.append(
                        delimiter.join(group)
                    )

                return output

            return cls.apply_one(
                values,
                {
                    "capability": capability,
                    "arguments": arguments,
                },
            )

        def process(lines: Iterable[str]):
            chunk = []

            for line in lines:
                chunk.append(line)

                if len(chunk) >= chunk_size:
                    values = chunk
                    chunk = []

                    for (
                        _operation,
                        capability,
                        arguments,
                        state,
                    ) in parsed:
                        values = apply_stream_operation(
                            values,
                            capability,
                            arguments,
                            state,
                        )

                    for value in values:
                        yield value

            if chunk:
                values = chunk

                for (
                    _operation,
                    capability,
                    arguments,
                    state,
                ) in parsed:
                    values = apply_stream_operation(
                        values,
                        capability,
                        arguments,
                        state,
                    )

                for value in values:
                    yield value

            # Flush stateful operations in operation order.
            #
            # This is especially important for join_blocks, where the final
            # partial group must still be emitted.
            for index, (
                _operation,
                capability,
                arguments,
                state,
            ) in enumerate(parsed):
                if capability != "format.join_blocks":
                    continue

                pending = state["pending"]

                if not pending:
                    continue

                output = [
                    state["delimiter"].join(
                        pending
                    )
                ]

                state["pending"] = []

                # The pending output belongs at this operation's position,
                # so pass it through operations that occur after it.
                for (
                    _later_operation,
                    later_capability,
                    later_arguments,
                    later_state,
                ) in parsed[index + 1:]:
                    output = apply_stream_operation(
                        output,
                        later_capability,
                        later_arguments,
                        later_state,
                    )

                for value in output:
                    yield value

        return process