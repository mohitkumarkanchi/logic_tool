#!/usr/bin/env bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LogicTool — Complete Setup & Usage Guide
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ─── 1. INITIAL SETUP ───────────────────────────

# Create .python-version
echo "3.11" > .python-version

# Initialize project with uv
uv sync

# Setup environment
cp .env.example .env
# Edit .env with your API key:
#   ANTHROPIC_API_KEY=sk-ant-...
#   or
#   GEMINI_API_KEY=AIza...

# ─── 2. VERIFY SETUP ────────────────────────────

# Check domains are configured
uv run logictool domains
# Output:
#   Domains: 30+
#   Estimated snippets: 1100+
#   Generation tasks: 300+

# Run tests
uv run pytest tests/ -v

# ─── 3. GENERATE SNIPPETS ───────────────────────

# Option A: Generate ALL domains at once (~2-3 min, ~$2 API cost)
uv run logictool generate --provider claude --concurrency 10

# Option B: Generate one domain at a time (for testing)
uv run logictool generate --provider claude --domain strings
uv run logictool generate --provider gemini --domain pandas

# Option C: Mix providers for cost optimization
#   Use Gemini (cheaper) for basic/medium, Claude for advanced
uv run logictool generate --provider gemini --domain data_structures
uv run logictool generate --provider claude --domain ml_sklearn

# Check what was generated
ls -la data/raw/
# strings__python__basic.json
# strings__python__medium.json
# strings__cpp__basic.json
# ...

# ─── 4. IMPORT TO DATABASE ──────────────────────

uv run logictool import
# Output:
#   ✓ strings__python__basic.json → 8 snippets
#   ✓ strings__python__medium.json → 7 snippets
#   ...
#   Total imported: 1100+ snippets

# ─── 5. BUILD SEARCH INDEX ──────────────────────

uv run logictool rebuild-index
# Output:
#   Loading embedding model: all-MiniLM-L6-v2...
#   Building embedding index for 1100 snippets...
#   Index built: 1100 vectors, dim=384, size=1650.0 KB
#   Index saved: data/embeddings.npz

# ─── 6. SEARCH! ─────────────────────────────────

# Hybrid search (semantic + keyword — best quality)
uv run logictool search "read csv skip first row"
uv run logictool search "compare strings ignore case"
uv run logictool search "draw bounding box on image"
uv run logictool search "retry failed api call"
uv run logictool search "ARIMA forecast next 30 days"

# Filter by language
uv run logictool search "sort array" --lang python
uv run logictool search "sort array" --lang cpp

# Filter by domain
uv run logictool search "group by sum" --domain pandas
uv run logictool search "basic auth" --domain fastapi

# Filter by complexity
uv run logictool search "regex" --complexity basic
uv run logictool search "regex" --complexity advanced

# Pure semantic mode (best for natural language queries)
uv run logictool search "how to cache function results" --mode semantic

# Pure keyword mode (best for exact term lookup)
uv run logictool search "lru_cache" --mode keyword

# Combine all filters
uv run logictool search "model training" --lang python --domain ml_sklearn --complexity medium -n 3

# ─── 7. BROWSE ───────────────────────────────────

# Browse by domain
uv run logictool browse --domain opencv
uv run logictool browse --domain yolo --complexity basic
uv run logictool browse --lang bash --domain ssh_linux

# ─── 8. MANAGE ───────────────────────────────────

# View stats
uv run logictool stats

# Get a specific snippet by ID
uv run logictool get abc123def456

# Add a snippet manually
uv run logictool add

# Delete a snippet
uv run logictool delete abc123def456

# Export everything as JSON backup
uv run logictool export --output-dir data/backup

# ─── 9. DAILY WORKFLOW ───────────────────────────

# Quick alias (add to .bashrc/.zshrc)
alias lt="uv run logictool search"
alias ltb="uv run logictool browse"

# Now just:
lt "read excel file pandas"
lt "ssh tunnel remote port"
lt "yolo inference video"
lt "fastapi jwt auth"
ltb --domain python_stdlib --complexity medium