from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import observe, get_client

    class _LangfuseContextCompat:
        """Compatibility wrapper for langfuse v4 API."""

        def update_current_trace(self, **kwargs: Any) -> None:
            """In v4, trace-level updates use the client directly."""
            try:
                client = get_client()
                # v4 doesn't have update_current_trace, use tags via span
                pass
            except Exception:
                pass

        def update_current_observation(self, **kwargs: Any) -> None:
            """In v4, use update_current_span or update_current_generation."""
            try:
                client = get_client()
                if hasattr(client, "update_current_span"):
                    client.update_current_span(**kwargs)
            except Exception:
                pass

        def flush(self) -> None:
            try:
                client = get_client()
                client.flush()
            except Exception:
                pass

    langfuse_context = _LangfuseContextCompat()

except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

        def flush(self) -> None:
            return None

    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
