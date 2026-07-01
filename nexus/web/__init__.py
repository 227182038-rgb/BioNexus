"""Web UI — minimal Jinja2-rendered interface.

This is a thin web UI on top of the FastAPI app in :mod:`nexus.api`.
The UI supports:

- Asking a question to the default agent
- Viewing the interpretation with citations
- Browsing the project's claim graph
"""

from __future__ import annotations
