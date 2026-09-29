from .contracts import Operation
from .runtime import HashtagOperationRuntime


class Sandbox:
    """
    Core simulation layer.

    Sandbox remains the public simulation interface used by the existing
    V7-V10 architecture, but execution semantics now live in the shared
    HashtagOperationRuntime.
    """

    def apply(self, text, actions):
        return HashtagOperationRuntime.apply(
            text,
            actions,
        )

    def apply_operations(self, text, operations):
        return HashtagOperationRuntime.apply(
            text,
            operations,
        )