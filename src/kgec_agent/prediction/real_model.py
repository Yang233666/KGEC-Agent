"""Lazy extension point for a separately installed real KGE implementation."""

from __future__ import annotations

from typing import Protocol

from kgec_agent.schemas.models import PredictionResult, StructuredQuery


class RealModelAdapter(Protocol):
    def predict_link(self, query: StructuredQuery) -> PredictionResult: ...


def load_real_model_adapter(import_path: str) -> RealModelAdapter:
    """Load an explicitly selected adapter without importing it in offline mode."""
    import importlib

    module_name, attribute = import_path.rsplit(":", 1)
    factory = getattr(importlib.import_module(module_name), attribute)
    return factory()
