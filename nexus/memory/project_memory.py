"""Project memory — per-project memory of artifacts, settings, and history."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ProjectMemory:
    """Per-project memory persisted as a JSON file.

    A project is a logical unit of research work (e.g. "BRCA1
    mechanism study"). Project memory stores:

    - Project ID, name, description
    - Settings (default provider, model, audience level)
    - Artifact references (BioKit run IDs, claim IDs, report paths)
    - Event history (a timestamped log of project events)
    """

    id: str = field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:12]}")
    name: str = "Untitled project"
    description: str = ""
    created_at: float = field(default_factory=time.time)
    settings: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    _path: Path | None = field(default=None, repr=False)

    @classmethod
    def load(cls, path: str | Path) -> ProjectMemory:
        """Load a project from a JSON file."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Project file not found: {p}")
        data = json.loads(p.read_text(encoding="utf-8"))
        proj = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        proj._path = p
        return proj

    def save(self, path: str | Path | None = None) -> Path:
        """Save the project to a JSON file."""
        p = Path(path) if path else self._path
        if p is None:
            raise ValueError("No path provided and no previous path known")
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "settings": self.settings,
            "artifacts": self.artifacts,
            "history": self.history,
        }
        p.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        self._path = p
        return p

    def record_event(self, event_type: str, details: dict[str, Any] | None = None) -> None:
        """Append an event to the project history."""
        self.history.append(
            {
                "timestamp": time.time(),
                "type": event_type,
                "details": details or {},
            }
        )

    def add_artifact(self, name: str, uri: str) -> None:
        """Add or update a named artifact reference."""
        self.artifacts[name] = uri
        self.record_event("artifact_added", {"name": name, "uri": uri})

    def get_artifact(self, name: str) -> str | None:
        return self.artifacts.get(name)

    def set_setting(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.record_event("setting_changed", {"key": key, "value": value})

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)


__all__ = ["ProjectMemory"]
