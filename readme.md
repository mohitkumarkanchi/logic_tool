# LogicTool

**Offline semantic code snippet manager with pre-curated developer primitives.**

A lightweight CLI tool that stores 1000+ curated code snippets in SQLite, pre-computes S-BERT embeddings, and serves instant semantic search from your terminal. No internet needed at search time.

## Why This Exists

LLMs are making developers passive. You prompt, paste, move on — and six months later you can't write a basic groupby without asking again. LogicTool flips that: **recall, not generation**. Your vetted snippets, your organization, millisecond retrieval, zero hallucination.

**What makes it different from existing snippet managers:**

- **Pre-curated library** — 1000+ universal developer primitives, not an empty container
- **Semantic search** — "how to cache function results" finds `lru_cache` even without exact keyword match
- **Complexity-organized** — basic → medium → advanced across 30+ domains
- **Offline-first** — works on planes, air-gapped machines, restricted networks
- **Recall-oriented** — every snippet includes a "why this works" explanation to reinforce understanding

## Domains Covered

**Core Logic:** Strings, Numbers, Data Structures, Regex, File I/O, Date/Time, Error Handling, Concurrency

**Python Stdlib:** contextlib, functools, itertools, collections, pathlib, Pydantic, typing patterns

**Data & ML:** Pandas, NumPy, Scikit-learn, PyTorch, Time Series (ARIMA/SARIMAX/Prophet), Visualization

**Computer Vision:** OpenCV, YOLO, Bounding Box utilities, Annotation format converters

**LLM SDKs:** OpenAI, Gemini, Anthropic — client setup, tool use, streaming, RAG patterns

**Backend:** FastAPI, Database (SQLite/Postgres/Redis/MongoDB), Networking, Serialization, Security, Web Scraping

**DevOps:** Bash Scripting, SSH & Linux Commands, Git, Docker, Testing (Pytest), Environment & Config

**Frontend:** HTML/CSS/JS from static pages to switchable dashboards

**Languages:** Python, C++, Bash, JavaScript/HTML

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **API Key** — either Anthropic (Claude) or Google (Gemini) for snippet generation

### Install uv (if not installed)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Setup

### 1. Organize Project Files

If you downloaded all files flat into a `logic_tool/` directory:

```bash
cd logic_tool
chmod +x organize.sh
./organize.sh
```

This creates the full directory structure, moves files into place, and creates all `__init__.py` files.

### 2. Configure API Key

```bash
# Edit .env with your preferred editor
nano .env
```

Add **one** of:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
GEMINI_API_KEY=AIza-your-key-here
```

You only need one provider. Claude produces slightly higher quality snippets, Gemini is cheaper and faster.

### 3. Install Dependencies

```bash
uv sync
```

This creates a virtual environment and installs all dependencies. First run downloads ~80MB for the S-BERT model.

### 4. Verify Installation

```bash
# Check domain config
uv run logictool domains

# Run tests
uv run pytest tests/ -v
```

## Usage

### Generate Snippets

The generation pipeline calls the LLM API in parallel to create all snippets.

```bash
# Generate ALL domains at once (~300 API calls, ~2-3 min, ~$2 cost)
uv run logictool generate --provider claude

# Generate a single domain (for testing or incremental build)
uv run logictool generate --provider claude --domain strings
uv run logictool generate --provider gemini --domain pandas

# Control parallelism
uv run logictool generate --provider claude --concurrency 5
```

**Cost estimates:**
- Claude Sonnet: ~$2-3 for all domains
- Gemini Flash: ~$0.50-1 for all domains

**Mix providers for cost optimization:**
```bash
# Gemini for basic/medium (cheaper), Claude for complex domains
uv run logictool generate --provider gemini --domain data_structures
uv run logictool generate --provider claude --domain ml_sklearn
```

### Import to Database

After generation, import the JSON files into SQLite:

```bash
uv run logictool import
```

Output:
```
  ✓ strings__python__basic.json → 8 snippets
  ✓ strings__python__medium.json → 7 snippets
  ✓ strings__cpp__basic.json → 6 snippets
  ...
  Total imported: 1100+ snippets
```

### Build Search Index

Generate S-BERT embeddings for semantic search:

```bash
uv run logictool rebuild-index
```

Output:
```
Loading embedding model: all-MiniLM-L6-v2...
Building embedding index for 1100 snippets...
Index built: 1100 vectors, dim=384, size=1650.0 KB
Index saved: data/embeddings.npz
```

This is a one-time operation. Re-run only after adding new snippets.

### Search

The primary way to use LogicTool. Three search modes available:

```bash
# Hybrid search (default — best quality, combines semantic + keyword)
uv run logictool search "read csv skip first row"
uv run logictool search "compare strings ignore case"
uv run logictool search "draw bounding box on image"
uv run logictool search "retry failed api call with backoff"
uv run logictool search "ARIMA forecast next 30 days"

# Pure semantic (best for natural language queries)
uv run logictool search "how to cache function results" --mode semantic

# Pure keyword (best for exact term lookup)
uv run logictool search "lru_cache" --mode keyword
```

**Filter results:**

```bash
# By language
uv run logictool search "sort array" --lang python
uv run logictool search "sort array" --lang cpp

# By domain
uv run logictool search "group by sum" --domain pandas

# By complexity
uv run logictool search "regex" --complexity basic

# Combine filters
uv run logictool search "model training" -l python -d ml_sklearn -c medium -n 3
```

### Browse

Explore snippets by category without a search query:

```bash
uv run logictool browse --domain opencv
uv run logictool browse --domain yolo --complexity basic
uv run logictool browse --lang bash --domain ssh_linux
uv run logictool browse --complexity advanced --lang python
```

### Manage Snippets

```bash
# View library statistics
uv run logictool stats

# View a specific snippet in full detail
uv run logictool get <snippet-id>

# Add a snippet manually (interactive)
uv run logictool add

# Delete a snippet
uv run logictool delete <snippet-id>

# Export everything as JSON backup
uv run logictool export --output-dir data/backup
```

### List All Configured Domains

```bash
uv run logictool domains
```

## Daily Workflow

Add these aliases to your `.bashrc` or `.zshrc`:

```bash
alias lt="uv run logictool search"
alias ltb="uv run logictool browse"
alias lts="uv run logictool stats"
```

Then just:

```bash
lt "read excel file pandas"
lt "ssh tunnel remote port"
lt "yolo inference video"
lt "fastapi jwt auth middleware"
lt "pytorch custom dataset" --complexity medium
ltb --domain python_stdlib
```

## Architecture

### Design Patterns

**Factory Pattern** — `LLMFactory.create("claude")` or `LLMFactory.create("gemini")`. Add new providers by implementing `BaseLLMProvider` and registering with the factory.

**Repository Pattern** — `BaseSnippetRepository` defines the data access interface. `SQLiteSnippetRepository` is the concrete implementation. Swap to Postgres or any other backend without touching business logic.

**Data Model Pattern** — Pydantic models everywhere: `Snippet`, `SnippetMetadata`, `SnippetBatch`, `DomainDefinition`. Everything is typed, validated, and JSON-serializable.

### Project Structure

```
logictool/
├── src/logictool/
│   ├── models/          # Pydantic data models & enums
│   ├── llm/             # LLM provider abstraction & factory
│   ├── repository/      # Data access layer (SQLite, JSON)
│   ├── services/        # Business logic (validation, embedding)
│   ├── pipeline/        # Generation pipeline (parallel runner, prompts)
│   ├── search/          # Search engines (semantic, keyword, hybrid)
│   ├── config/          # Settings & domain definitions
│   └── cli/             # Typer CLI commands & display
├── data/
│   ├── raw/             # Generated JSON files (intermediate)
│   ├── snippets.db      # SQLite database (main storage)
│   └── embeddings.npz   # Pre-computed S-BERT vectors
└── tests/
```

### Search Architecture

LogicTool uses a three-layer search strategy:

1. **Keyword search (FTS5)** — SQLite full-text search on title, description, tags. Handles exact term lookups.

2. **Semantic search (S-BERT)** — `all-MiniLM-L6-v2` encodes queries and snippets into 384-dim vectors. Cosine similarity finds conceptually related snippets even without keyword overlap.

3. **Hybrid search (RRF)** — Reciprocal Rank Fusion merges keyword and semantic results. Gives fair weight to both exact matches and semantic matches. This is the default and recommended mode.

### Data Flow

```
Generation:  Domain Config → LLM API (parallel) → JSON files → SQLite → Embeddings
Search:      User Query → Embed → Cosine Similarity + FTS5 → RRF Merge → Display
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | One of these |
| `GEMINI_API_KEY` | Google API key for Gemini | is required |
| `CLAUDE_MODEL` | Override Claude model (default: `claude-sonnet-4-20250514`) | No |
| `GEMINI_MODEL` | Override Gemini model (default: `gemini-2.5-flash`) | No |

### config.yaml (optional overrides)

All settings can also be configured via environment variables. The `Settings` class uses Pydantic BaseSettings with `.env` file support.

## Extending

### Add a New Domain

Edit `src/logictool/config/domains.py` and add a new `DomainDefinition` to the `DOMAINS` list:

```python
DomainDefinition(
    name="your_domain",
    display_name="Your Domain Name",
    description="What this domain covers",
    applicable_languages=[Language.PYTHON, Language.BASH],
    complexity_hints={
        Complexity.BASIC: ["hint1", "hint2"],
        Complexity.MEDIUM: ["hint3", "hint4"],
        Complexity.ADVANCED: ["hint5", "hint6"],
    },
    estimated_snippets=15,
)
```

Then generate: `uv run logictool generate --provider claude --domain your_domain`

### Add a New LLM Provider

1. Create `src/logictool/llm/your_provider.py` implementing `BaseLLMProvider`
2. Register it in `LLMFactory._registry`
3. Add the enum value to `LLMProvider` in `enums.py`

### Add a New Repository Backend

Implement `BaseSnippetRepository` with your storage backend (e.g., PostgreSQL, MongoDB). The rest of the application uses the interface, so no other changes needed.

## Troubleshooting

### "No embedding index found"
Run `uv run logictool rebuild-index` after importing snippets.

### "ANTHROPIC_API_KEY not set"
Ensure your `.env` file has the key set. Check with: `cat .env`

### Generation fails for some tasks
The pipeline retries 3 times per task. Failed tasks are listed in the summary. Re-run generation for the specific domain: `uv run logictool generate --domain <failed_domain>`

### Search returns no results
- Check if snippets are imported: `uv run logictool stats`
- Rebuild the index: `uv run logictool rebuild-index`
- Try keyword mode: `uv run logictool search "your query" --mode keyword`

### Import/export encoding issues
All files use UTF-8 encoding. Ensure your terminal supports it.

## Snippet Anatomy

Every snippet in LogicTool has:

```
┌─────────────────────────────────────────────┐
│ Title:       Case insensitive string compare │
│ Description: Compare two strings ignoring    │
│              case using lower()              │
│ Language:    Python                          │
│ Domain:      strings / comparison            │
│ Complexity:  basic                           │
│ Tags:        #string #compare #case          │
│ Why:         lower() normalizes both strings │
│              before comparison               │
│                                              │
│ Code:                                        │
│   def iequal(a: str, b: str) -> bool:       │
│       return a.lower() == b.lower()          │
└─────────────────────────────────────────────┘
```

The **"Why"** field is intentional — it reinforces understanding every time you look something up. Over time, you'll need the tool less. That's the whole point.

## License

MIT