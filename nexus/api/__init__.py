"""Nexus REST API (FastAPI)."""

from __future__ import annotations

from nexus.api.app import app, get_nexus, set_nexus

__all__ = ["app", "get_nexus", "set_nexus"]
