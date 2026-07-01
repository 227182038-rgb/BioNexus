# Quickstart

## Install

```bash
# From PyPI (when published)
pip install nexus-bii

# Or from source
git clone https://github.com/nexus-bii/nexus.git
cd nexus
pip install -e ".[dev]"
```

## Hello Nexus

```python
from nexus.sdk import quickstart
from nexus.providers.dummy import DummyProvider

nx = quickstart(provider=DummyProvider())
result = nx.interpret("What is known about BRCA1?")
print(result.answer)
print(f"Confidence: {result.confidence.value:.2f}")
```

## Use a real LLM provider

```python
from nexus.sdk import Nexus
from nexus.providers.openai_provider import OpenAIProvider

nx = Nexus(provider=OpenAIProvider(model="gpt-4o-mini"))
result = nx.interpret("What does a BLAST hit to BRCA1 suggest about my query?")
```

## Index literature and ask a cited question

```python
from nexus.sdk import Nexus
from nexus.providers.dummy import DummyProvider

nx = Nexus(provider=DummyProvider())

# Index some text (in production, use the knowledge clients)
nx.index_text(
    source_uri="pubmed:12345",
    title="BRCA1 and homologous recombination repair",
    content="BRCA1 is essential for homologous recombination repair of DNA double-strand breaks.",
    metadata={"pmid": "12345", "year": "2024"},
)

result = nx.interpret("What is BRCA1's role in DNA repair?")
for citation in result.citations:
    print(citation)
```

## Use the CLI

```bash
# Ask a question
nexus interpret --question "What is BRCA1?" --provider dummy

# Index a document
nexus index --uri pubmed:1 --title "BRCA1 paper" --content "BRCA1 repairs DNA."

# Search the index
nexus search --query "BRCA1"

# Generate a report
nexus report --title "BRCA1 study" \
  --question "What is BRCA1?" \
  --question "How does it repair DNA?" \
  --output report.md

# Start the REST API
nexus serve --port 8000
```

## Use the REST API

```bash
# Start the server
nexus serve --port 8000

# In another terminal
curl -X POST http://localhost:8000/api/interpret \
  -H "Content-Type: application/json" \
  -d '{"question": "What is BRCA1?"}'
```

## Use the FastAPI app directly

```python
from nexus.api.app import app, set_nexus
from nexus.sdk import Nexus
from nexus.providers.dummy import DummyProvider

set_nexus(Nexus(provider=DummyProvider()))

# Now `app` is a standard FastAPI app — mount it in any ASGI server.
import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8000)
```

## Integrate with BioKit

```python
from nexus.core.biokit import InProcessBioKit
from nexus.sdk import Nexus
from nexus.providers.dummy import DummyProvider

# Define a deterministic BioKit program
class EchoProgram:
    name = "echo"
    def run(self, inputs):
        return {"echo": inputs.get("message", "")}

biokit = InProcessBioKit()
biokit.register_program(EchoProgram())

nx = Nexus(provider=DummyProvider(), biokit=biokit)

# Invoke BioKit through Nexus — output is auto-registered as evidence
output = nx.run_biokit("echo", {"message": "hello"})
print(output.outputs)  # {'echo': 'hello'}
```

## Next steps

- [Architecture overview](architecture.md)
- [CLI reference](cli.md)
- [REST API reference](rest_api.md)
- [Providers guide](guides/providers.md)
- [Agents guide](guides/agents.md)
