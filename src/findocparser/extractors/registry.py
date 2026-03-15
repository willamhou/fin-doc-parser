"""Extractor registry — maps doc_type to extractor class."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.generic import GenericExtractor

_REGISTRY: dict[str, type[BaseExtractor]] = {}


def register_extractor(cls: type[BaseExtractor]) -> type[BaseExtractor]:
    """Decorator to register an extractor."""
    instance = cls()
    _REGISTRY[instance.doc_type] = cls
    return cls


def get_extractor(doc_type: str) -> BaseExtractor:
    """Get an extractor instance by document type.

    Falls back to GenericExtractor for unknown types.
    """
    # Lazy import to register all built-in extractors
    _ensure_registered()

    cls = _REGISTRY.get(doc_type)
    if cls is None:
        return GenericExtractor()
    return cls()


_registered = False


def _ensure_registered() -> None:
    """Import all extractor modules to trigger registration."""
    global _registered
    if _registered:
        return
    _registered = True

    import findocparser.extractors.bank_statement  # noqa: F401
    import findocparser.extractors.business_license  # noqa: F401
    import findocparser.extractors.financial_statement  # noqa: F401
