# REST API reference

Nexus exposes a FastAPI-based REST API. Start it with:

```bash
nexus serve --port 8000
```

Interactive docs (Swagger UI) are available at `http://localhost:8000/docs`.

## Endpoints

### `GET /`

Returns the minimal web UI (single-page HTML).

### `GET /api/health`

Health check.

**Response:**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "agents": ["experiment", "literature", "report", "validation", "workflow"],
  "provider": "dummy"
}
```

### `GET /api/agents`

List registered agents.

**Response:** `["experiment", "literature", "report", "validation", "workflow"]`

### `POST /api/interpret`

Ask Nexus a question.

**Request:**

```json
{
  "question": "What is BRCA1?",
  "agent": "literature",
  "context": {}
}
```

**Response:**

```json
{
  "answer": "BRCA1 is a tumor suppressor gene...",
  "confidence": 0.75,
  "provider_model": "openai/gpt-4o-mini",
  "citations": ["https://pubmed.ncbi.nlm.nih.gov/..."],
  "contradictions": [],
  "recommended_next_step": "Cross-reference against UniProt.",
  "evidence_ids": ["ev_abc123"]
}
```

### `POST /api/validate`

Validate a claim against literature.

**Request:**

```json
{
  "claim": "BRCA1 is unrelated to DNA repair.",
  "context": {}
}
```

### `POST /api/index`

Index a document into the RAG retriever.

**Request:**

```json
{
  "source_uri": "pubmed:12345",
  "title": "BRCA1 paper",
  "content": "BRCA1 is involved in DNA repair.",
  "metadata": {"pmid": "12345"}
}
```

### `GET /api/search`

Search the RAG index.

**Query parameters:**

- `q` — search query
- `limit` — max results (default 5)

**Response:**

```json
{
  "query": "BRCA1",
  "results": [
    {
      "document_id": "pubmed:1",
      "title": "BRCA1 paper",
      "source_uri": "pubmed:12345",
      "score": 1.234,
      "snippet": "...BRCA1 is involved...",
      "citation": "Smith J, Doe A (2024). BRCA1 paper. Nature. PMID:12345."
    }
  ]
}
```

### `POST /api/biokit`

Run a registered BioKit program.

**Request:**

```json
{
  "program": "echo",
  "inputs": {"message": "hello"}
}
```

### `POST /api/report`

Generate a publication-quality report.

**Request:**

```json
{
  "title": "BRCA1 study",
  "questions": ["What is BRCA1?", "How does it repair DNA?"]
}
```

**Response:**

```json
{
  "title": "BRCA1 study",
  "markdown": "# BRCA1 study\n\n## Summary\n...",
  "n_sections": 4
}
```

## Embedding the API in another FastAPI app

```python
from fastapi import FastAPI
from nexus.api.app import app as nexus_app, set_nexus
from nexus.sdk import Nexus
from nexus.providers.dummy import DummyProvider

main_app = FastAPI()
set_nexus(Nexus(provider=DummyProvider()))
main_app.mount("/nexus", nexus_app)
```
