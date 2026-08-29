# Chronicle

**Local-first developer intelligence.** Chronicle records how a software project changes over time, turns that history into signals, and lets you ask questions about it — all stored and analyzed on your own machine.

Chronicle fits naturally into your existing workflow. Point it at a Git project, and it:

1. **Scans** your project's history into structured *observations* (git commits, Django migrations).
2. **Analyzes** those observations into actionable *findings* (new files, changed schema fields …).
3. **Interprets** the collected history with AI, answering questions in plain language.

## How it works

```
git history ──► scan ──► observations ──► analyze ──► findings ──► interpret (AI) ──► answers
Django migrations ─┘                     local SQLite     ▲
                                                     keywords + related commits
```

- **Local-first** — everything lives in a `.chronicle/` folder inside your project. No accounts, no cloud sync, no telemetry. Your `chronicle.db` stays yours.
- **Incremental** — Chronicle remembers how far it got (`scan_state` for scanners, `analysis_state` for analyzers) so repeated runs only process what's new.
- **Extensible** — scanners (`Scanner`) and analyzers (`BaseAnalyzer`) are pluggable; providers are pluggable too (OpenAI / Gemini).

## Requirements

- **Python 3.10+**
- A **Git** repository (the project root is detected by walking up to the nearest `.git` directory)
- `pip` via the `dev` extra for running tests

## Installation

```bash
# clone and enter the repository
git clone https://github.com/Sakshyam-Xtha/Chronicle.git
cd Chronicle

# create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate

# install in editable mode (includes the `chronicle` command)
pip install -e ".[dev]"
```

Verify the CLI is on your path:

```bash
chronicle version   # -> Chronicle 0.1.0
```

## Quick start

```bash
# 1. Initialize Chronicle in a project (creates .chronicle/ + local DB)
cd /path/to/your/project
chronicle init

# 2. Scan the project history into observations
chronicle scan

# 3. Browse what was recorded
chronicle show
chronicle show --id 1

# 4. Analyze observations into findings
chronicle analyze

# 5. Ask questions about your history (requires an AI provider/key)
chronicle interpret --question "When did we add the User model?"
```

> `init`, `scan`, and `show` need no configuration. Only `interpret` requires an AI provider.

## Command reference

| Command | Description |
| --- | --- |
| `chronicle init` | Create the `.chronicle/` directory and initialize the local database |
| `chronicle scan` | Scan project history into observations (git commits, Django migrations) |
| `chronicle show` | List all observations; `--id <n>` shows one observation in detail |
| `chronicle analyze` | Turn observations into findings via the installed analyzers |
| `chronicle interpret --question "<text>"` | Ask an AI-backed question about the project history |
| `chronicle config` | View current configuration; `set provider` / `set model` to configure AI |
| `chronicle status` | Show whether the project is initialized and detected |
| `chronicle version` | Print the Chronicle version |

### `chronicle status`

```bash
$ chronicle status
Project: my-project
Root: /path/to/my-project
Git: detected
Chronicle: initialized
Configuration: found
```

### `chronicle show`

Without arguments it prints a compact table of all observations. With `--id <n>` it renders a detailed view:

```text
Observation #1
────────────────────────────────────────────
Source:       git
Type:         commit
External ID:  9f8d3a1
Timestamp:    2026-08-21 12:00:00 UTC

Data
────────────────────────────────────────────
```
Migration observations additionally show **App**, **Migration**, **Dependencies**, and **Operations** (model / field per operation).

## Configuring AI (for `interpret`)

Chronicle reads its configuration from `.chronicle/config.toml`:

```toml
[chronicle]
version = 1

[ai]
provider = ""
model = ""
```

Set the provider and model:

```bash
chronicle config set provider openai
chronicle config set model gpt-4o
```

Then export your API key as an environment variable:

```bash
export OPENAI_API_KEY="sk-..."     # provider: openai
export GEMINI_API_KEY="..."        # provider: gemini
```

Check everything is wired up:

```bash
chronicle config
```

## What gets recorded

### Git commits (`scan`)

Each commit becomes an observation with:

- `hash`, `message`, `author`
- `parents` (empty for the root commit, one or more for merges)
- `changes` — per-file **status** (`A` added, `M` modified, `D` deleted) and **path**

### Django migrations (`scan`)

Every `migrations/*.py` file (ignoring `.git`, `.venv`, `venv`, `env`, `node_modules`, `__pycache__`) is parsed with `ast` into an observation with:

- `app` (application label), `name` (migration name)
- `dependencies`
- `operations` — e.g. `AddField`, `RemoveField` with model / field details

### Findings (`analyze`)

Analyzers turn observations into findings:

- **GitAnalyzer** — flags newly created files (`A`) with `severity: info`
- **DjangoMigrationAnalyzer** — flags `RemoveField` (`warning`) and `AddField` (`info`) operations

## How interpretation works

`chronicle interpret` does **not** dump everything at the model. It:

1. Tokenizes your question and drops stop words to extract keywords.
2. Scores every finding by how well it matches those keywords (title, message, data).
3. Picks the top 10 findings and their related git commits (e.g. the commit that introduced a migration).
4. Builds a prompt with only that focused context and asks the configured provider.

## Project layout

```
src/chronicle/
├── ai/              # AI provider abstraction (OpenAI, Gemini, factory)
├── analysis/        # analyzers + engine that turn observations into findings
├── cli/             # Typer CLI commands (`scan`, `show`, `analyze`, …)
├── config/          # config.toml management + API key resolution
├── integrations/    # thin wrappers (e.g. git)
├── interpretation/  # question -> context -> prompt -> AI response
├── project/         # discovery, initialization, status
├── scanning/        # scanners + engine that collect observations
│   └── scanners/    # git, django_migrations and their models
└── storage/         # SQLite repositories + schema
```

## Development

Run the test suite:

```bash
pip install -e ".[dev]"
pytest test/
```

The suite is split into:

- `test/unit/` — fast, mocked tests (parsing, storage, contexts, models)
- `test/integration/` — real-git and end-to-end CLI tests (incremental scan checkpoints, migration parsing, merge parents)

## Roadmap / status

Chronicle is an early-stage local-first tool (`0.1.0`). Current scanners cover **git** and **Django migrations**; analyzers cover **git file additions** and **Django schema changes**; AI interpretation supports **OpenAI** and **Gemini**.

## License

Not yet specified.
