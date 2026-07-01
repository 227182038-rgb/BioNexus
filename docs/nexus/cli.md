# CLI reference

The `nexus` command-line interface is built with [Typer](https://typer.tiangolo.com/) and provides commands for all common operations.

## Installation

```bash
pip install nexus-bii
```

The `nexus` command is available on your PATH after installation.

## Commands

### `nexus version`

Print the Nexus version.

### `nexus providers`

List available LLM providers.

### `nexus agents`

List registered agents.

### `nexus interpret`

Ask Nexus a question.

```bash
nexus interpret \
  --question "What is BRCA1?" \
  --agent literature \
  --provider dummy
```

Options:

- `--question, -q` — The question to ask (required)
- `--agent, -a` — Agent to use (default: `literature`)
- `--provider, -p` — LLM provider name (auto-detected if omitted)
- `--model, -m` — LLM model name

### `nexus validate`

Validate a claim against literature.

```bash
nexus validate --claim "BRCA1 is unrelated to DNA repair."
```

### `nexus report`

Generate a publication-quality report from a set of questions.

```bash
nexus report \
  --title "BRCA1 study" \
  --question "What is BRCA1?" \
  --question "How does it repair DNA?" \
  --output report.md
```

### `nexus index`

Index a document into the RAG retriever.

```bash
nexus index \
  --uri pubmed:12345 \
  --title "BRCA1 paper" \
  --content "BRCA1 is involved in DNA repair." \
  --metadata '{"pmid": "12345"}'
```

The `--content` argument can be `@filename` to read from a file.

### `nexus search`

Search the RAG index.

```bash
nexus search --query "BRCA1" --limit 5
```

### `nexus biokit`

Run a registered BioKit program.

```bash
nexus biokit --program echo --inputs '{"message": "hello"}'
```

### `nexus serve`

Start the REST API server.

```bash
nexus serve --host 127.0.0.1 --port 8000
```

## Environment variables

Provider API keys are read from environment variables when not passed on the command line:

| Provider | Environment variable |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Gemini | `GOOGLE_API_KEY` |
| GLM (Zhipu) | `ZHIPUAI_API_KEY` |
| Ollama | `OLLAMA_API_KEY` (usually unused) |
| OpenRouter | `OPENROUTER_API_KEY` |

When `--provider` is omitted, Nexus auto-detects by picking the first provider with an API key set, falling back to the `dummy` provider.
