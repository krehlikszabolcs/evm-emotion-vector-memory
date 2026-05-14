# EVM — Evolution Vector Memory

## A deterministic interaction-state continuity framework for AI systems

Author: Szabolcs Krehlik  
ORCID: 0009-0003-8623-7876  
License: CC BY-NC-ND 4.0  
Contact: szabolcs.krehlik@gmail.com

This repository is a runnable experimental environment for **EVM (Evolution Vector Memory)**: a deterministic interaction-state continuity framework for AI systems. It provides a local web application with persistent storage, directed EV extraction, PEV/EEV/FEV tracking, memory recall, index logging, and diagnostics.

EVM is not a semantic vector database and not merely an affect or sentiment layer. It is a bounded trajectory architecture: every interaction is represented as a directed state transition, and long-running interaction identity is tracked through reconstructable PEV/EEV/FEV dynamics.

## Name clarification

The name **Evolution Vector Memory** replaces the earlier working name **Emotion Vector Memory**. The EVM abbreviation is preserved, but the full name is corrected to reflect the actual scope of the system: interaction continuity, bounded identity evolution, deterministic trajectory reconstruction, and stateful AI behavior across time. See [`NAME_CHANGE.md`](NAME_CHANGE.md) for the rationale.

The core interaction object is a directed EV time-slice:

`(x1, y1, z1, g1, e1, w1) -> (x2, y2, z2, g2, e2, w2)`

This repository is intended for research, inspection, testing, and demonstration. It is not presented as a production deployment.

## What is included

- Local Flask web app for chat-style interaction
- SQLite-backed persistence under `DATA/sqlite/`
- Plain NDJSON log mirrors under `DATA/logs/`
- EV entry/exit extraction per interaction
- PEV / EEV / FEV state tracking
- Pre-response planning and bounded state control
- Memory recall and indexed retrieval
- CIS export and diagnostics panel
- Provider support for OpenAI, xAI, and LM Studio

## Repository structure

```text
app/
  app.py                Flask routes and orchestration
  db.py                 SQLite access layer
  evm_core.py           EVM state update logic
  evm_spec.py           normative prompts and spec text
  indexing.py           turn summary and keyword indexing
  memory.py             retrieval helpers
  openai_client.py      provider adapter and model calls
app/templates/
  index.html            local web UI
DATA/
  logs/                 NDJSON mirrors created at runtime
  sqlite/               SQLite database created at runtime
install.command         first-time setup
start.command           start with provider from .env
start_openai.command    convenience launcher
start_lmstudio.command  convenience launcher
start_selector.command  provider chooser
run.py                  local server entry point
```

## Quick start

### macOS

1. Download or clone the repository.
2. Run `install.command`.
3. Fill in `.env` with your provider settings.
4. Run `start.command`.
5. Open `http://127.0.0.1:8765` if the browser does not open automatically.

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Provider configuration

Set the provider in `.env`:

```env
LLM_PROVIDER=openai
```

Supported values:
- `openai`
- `xai`
- `lmstudio`

Examples:

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_RESPONSE_MODEL=gpt-5.4
OPENAI_EXTRACTOR_MODEL=gpt-5.4
```

### xAI / Grok

```env
LLM_PROVIDER=xai
XAI_API_KEY=your_key_here
XAI_BASE_URL=https://api.x.ai/v1
XAI_RESPONSE_MODEL=grok-4-fast-reasoning
XAI_EXTRACTOR_MODEL=grok-4-fast-reasoning
```

### LM Studio

```env
LLM_PROVIDER=lmstudio
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_API_KEY=lm-studio
LMSTUDIO_RESPONSE_MODEL=local-model
LMSTUDIO_EXTRACTOR_MODEL=local-model
```

## Runtime data

Runtime data is not committed:

- SQLite database: `DATA/sqlite/evm.sqlite3`
- Log mirrors: `DATA/logs/*.ndjson`

If a log mirror file is missing or not writable, the application should continue and keep SQLite as the source of truth.

## Notes on the current implementation

- This repository is deliberately transparent rather than minimal.
- The current architecture favors observability and inspectability.
- Long-turn runs may require further optimization depending on provider, model, and context strategy.
- The repository is suitable as a public technical base for EVM demonstration and further iteration.

## Security and publishing notes

- Never commit `.env` or real API keys.
- Review `SECURITY_READ_FIRST.txt` before publishing or sharing.
- Review `LICENSE_NOTICE.txt` before commercial discussions or redistribution.

## License

This repository is shared under **CC BY-NC-ND 4.0** unless otherwise noted. See `LICENSE_NOTICE.txt` for the exact notice used in this package.
