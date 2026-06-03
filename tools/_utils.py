"""Utilitários internos compartilhados entre os módulos de tools."""

from __future__ import annotations

from datetime import datetime


def to_iso(date_str: str) -> str:
    """Converte DD/MM/YYYY → YYYY-MM-DD exigido pela API RHID."""
    return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")


def to_iso_optional(date_str: str | None) -> str | None:
    """Converte DD/MM/YYYY → YYYY-MM-DD; retorna None se entrada for None."""
    return to_iso(date_str) if date_str else None
