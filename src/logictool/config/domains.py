"""
All domain definitions for snippet generation.
Each domain defines what the LLM should generate.
Add new domains here — the pipeline picks them up automatically.
"""

from logictool.models.domain import DomainDefinition, SubDomain
from logictool.models.enums import Complexity, Language

DOMAINS: list[DomainDefinition] = [
    # ──────────────────────────────────────────────────
    # CORE LOGIC
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="strings",
        display_name="String & Text Manipulation",
        description="All string operations a developer encounters — comparison, search, transform, parsing",
        applicable_languages=[Language.PYTHON, Language.CPP, Language.BASH, Language.JAVASCRIPT],
        subdomains=[
            SubDomain(name="comparison", description="Equality, case-insensitive match"),
            SubDomain(name="search", description="Find, contains, startswith, endswith"),
            SubDomain(name="transform", description="Case conversion, trim, replace, reverse"),
            SubDomain(name="parsing", description="Split, tokenize, extract patterns"),
        ],
        complexity_hints={
            Complexity.BASIC: [
                "string equality comparison",
                "case insensitive compare",
                "concatenation with delimiter",
                "substring extraction / slicing",
                "trim whitespace",
                "case conversion (upper, lower, title)",
                "string search (find, contains, startsWith, endsWith)",
                "template interpolation / f-strings",
            ],
            Complexity.MEDIUM: [
                "regex match and extract with capture groups",
                "tokenization and word splitting",
                "encoding/decoding (base64, url encode, html escape)",
                "string padding and alignment",
                "multi-line string handling",
                "string to number and back conversion",
            ],
            Complexity.ADVANCED: [
                "fuzzy matching (Levenshtein distance)",
                "slug generation from unicode text",
                "efficient string building for large concatenations",
                "text wrapping and formatting",
                "natural sort (sort strings with numbers correctly)",
            ],
        },
        estimated_snippets=30,
    ),
    DomainDefinition(
        name="data_structures",
        display_name="Data Structures",
        description="Arrays, maps, sets, stacks, queues, trees, graphs — fundamental structures",
        applicable_languages=[Language.PYTHON, Language.CPP, Language.JAVASCRIPT],
        subdomains=[
            SubDomain(name="arrays", description="Sort, filter, map, reduce, deduplicate"),
            SubDomain(name="maps", description="Dict/HashMap operations, merge, invert"),
            SubDomain(name="sets", description="Union, intersection, difference"),
            SubDomain(name="stacks_queues", description="Stack, queue, deque patterns"),
        ],
        complexity_hints={
            Complexity.BASIC: [
                "array sort, reverse, slice",
                "array filter, map, reduce",
                "remove duplicates from array",
                "dict/map get, set, delete, iterate",
                "check if key exists in dict",
                "set union, intersection, difference",
            ],
            Complexity.MEDIUM: [
                "merge two dicts (shallow and deep)",
                "invert a dictionary (swap keys and values)",
                "group array of objects by key",
                "flatten nested list/array",
                "stack and queue implementations",
                "defaultdict and Counter patterns",
                "priority queue / heap operations",
            ],
            Complexity.ADVANCED: [
                "LRU cache implementation",
                "trie (prefix tree) basic operations",
                "graph adjacency list with BFS/DFS",
                "binary search on sorted array",
                "topological sort",
                "deep merge nested dicts",
            ],
        },
        estimated_snippets=30,
    ),
    # ──────────────────────────────────────────────────
    # DATABASE
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="database",
        display_name="Database Operations",
        description="SQL and NoSQL database primitives — CRUD, queries, connections",
        applicable_languages=[Language.PYTHON, Language.BASH],
        subdomains=[
            SubDomain(name="sqlite", description="SQLite connection, CRUD, FTS"),
            SubDomain(name="postgresql", description="psycopg2/asyncpg patterns"),
            SubDomain(name="redis", description="Redis get/set, pub/sub, cache"),
            SubDomain(name="mongodb", description="PyMongo connect, CRUD, aggregate"),
        ],
        complexity_hints={
            Complexity.BASIC: [
                "SQLite connect and create table",
                "basic INSERT, SELECT, UPDATE, DELETE",
                "parameterized queries (prevent SQL injection)",
                "Redis get/set with expiry",
                "MongoDB connect and insert document",
            ],
            Complexity.MEDIUM: [
                "JOIN queries (inner, left, right)",
                "GROUP BY with aggregation",
                "index creation and explain query",
                "transaction with commit/rollback",
                "connection pooling pattern",
                "Redis pub/sub pattern",
                "MongoDB find with filters and projection",
                "bulk insert operations",
            ],
            Complexity.ADVANCED: [
                "database migration pattern",
                "full text search setup",
                "MongoDB aggregation pipeline",
                "Redis cache-aside pattern with TTL",
                "async database operations (aiosqlite, asyncpg)",
                "upsert / ON CONFLICT patterns",
            ],
        },
        estimated_snippets=30,
    ),
    # ──────────────────────────────────────────────────
    # PANDAS & DATA
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="pandas",
        display_name="Pandas & Data Wrangling",
        description="DataFrame operations for data manipulation, cleaning, and analysis",
        applicable_languages=[Language.PYTHON],
        subdomains=[
            SubDomain(name="io", description="Read/write CSV, Excel, JSON, SQL"),
            SubDomain(name="selection", description="Filter, select, query rows and columns"),
            SubDomain(name="transform", description="Groupby, pivot, melt, merge, apply"),
            SubDomain(name="cleaning", description="Handle nulls, dtypes, duplicates"),
        ],
        complexity_hints={
            Complexity.BASIC: [
                "read CSV / Excel / JSON",
                "head, tail, info, describe, shape",
                "select columns, filter rows with conditions",
                "sort values, rename columns",
                "handle missing values (fillna, dropna)",
                "value_counts and basic stats",
            ],
            Complexity.MEDIUM: [
                "groupby with multiple aggregations",
                "merge / join two DataFrames",
                "pivot table and melt (wide to long)",
                "apply custom function to column",
                "string accessor operations (.str.contains, .str.split)",
                "dtype conversion and category optimization",
                "datetime column operations",
                "pandas to/from SQL (read_sql, to_sql)",
            ],
            Complexity.ADVANCED: [
                "multi-index operations",
                "window functions (rolling, expanding, ewm)",
                "method chaining pattern for clean pipelines",
                "memory optimization with categories and downcasting",
                "chunked reading for large files",
                "custom aggregation functions",
            ],
        },
        estimated_snippets=25,
    ),
    # ──────────────────────────────────────────────────
    # ML / DL
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="ml_sklearn",
        display_name="Machine Learning — Scikit-learn",
        description="ML primitives: preprocessing, model fitting, evaluation, pipelines",
        applicable_languages=[Language.PYTHON],
        complexity_hints={
            Complexity.BASIC: [
                "train_test_split",
                "StandardScaler / MinMaxScaler fit_transform",
                "LabelEncoder / OneHotEncoder",
                "LinearRegression fit and predict",
                "LogisticRegression fit and predict",
                "accuracy_score, confusion_matrix",
            ],
            Complexity.MEDIUM: [
                "Pipeline with scaler + model",
                "cross_val_score with multiple metrics",
                "GridSearchCV / RandomizedSearchCV",
                "classification_report",
                "feature importance from tree models",
                "RandomForest, KNN, SVM quick fit",
                "K-Means clustering",
                "PCA dimensionality reduction",
            ],
            Complexity.ADVANCED: [
                "ColumnTransformer for mixed types",
                "custom transformer class",
                "learning curves plot",
                "model calibration (CalibratedClassifierCV)",
                "stacking / voting ensemble",
                "SMOTE for imbalanced data",
            ],
        },
        estimated_snippets=25,
    ),
    DomainDefinition(
        name="time_series",
        display_name="Time Series Analysis",
        description="Statistical and ML approaches to time series forecasting",
        applicable_languages=[Language.PYTHON],
        subdomains=[
            SubDomain(name="preprocessing", description="Datetime index, resample, stationarity"),
            SubDomain(name="statistical", description="ARIMA, SARIMAX, exponential smoothing"),
            SubDomain(name="prophet", description="Facebook Prophet patterns"),
            SubDomain(name="dl_timeseries", description="LSTM and transformer time series"),
        ],
        complexity_hints={
            Complexity.BASIC: [
                "datetime index setup in pandas",
                "resample / frequency conversion",
                "rolling mean and std",
                "lag features creation",
                "time-based train/test split",
                "plot time series with matplotlib",
                "ADF stationarity test",
            ],
            Complexity.MEDIUM: [
                "ARIMA fit/predict/forecast",
                "SARIMAX with seasonal parameters",
                "auto_arima with pmdarima",
                "ACF/PACF plot for parameter selection",
                "seasonal decomposition (trend/seasonal/residual)",
                "Prophet basic fit/predict",
                "Prophet add custom seasonality and holidays",
                "Holt-Winters exponential smoothing",
            ],
            Complexity.ADVANCED: [
                "walk-forward validation loop",
                "VAR for multivariate time series",
                "LSTM single step forecast in PyTorch",
                "sliding window dataset creation for DL",
                "feature engineering: lags, rolling stats, fourier terms",
                "time series specific metrics (MAPE, SMAPE)",
                "Prophet cross validation and performance metrics",
            ],
        },
        estimated_snippets=25,
    ),
    # ──────────────────────────────────────────────────
    # COMPUTER VISION
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="opencv",
        display_name="OpenCV & Computer Vision",
        description="Image and video processing primitives",
        applicable_languages=[Language.PYTHON, Language.CPP],
        subdomains=[
            SubDomain(name="basic_ops", description="Read, write, resize, crop, color convert"),
            SubDomain(name="processing", description="Threshold, edge detection, morphology"),
            SubDomain(name="detection", description="Contours, template matching, features"),
            SubDomain(name="video", description="Webcam capture, video read/write"),
        ],
        complexity_hints={
            Complexity.BASIC: [
                "read and display image",
                "save image to file",
                "resize image",
                "crop image region",
                "BGR to RGB to Grayscale conversion",
                "draw rectangle, circle, text on image",
                "webcam capture loop",
            ],
            Complexity.MEDIUM: [
                "Canny edge detection",
                "threshold (binary, adaptive, Otsu)",
                "contour detection and drawing",
                "blur / GaussianBlur / medianBlur",
                "morphological operations (erode, dilate, open, close)",
                "histogram equalization",
                "image rotation and affine transform",
            ],
            Complexity.ADVANCED: [
                "template matching",
                "ORB feature detection and matching",
                "perspective transform (4-point warp)",
                "optical flow (Lucas-Kanade)",
                "background subtraction (MOG2)",
                "video writer pipeline",
            ],
        },
        estimated_snippets=25,
    ),
    DomainDefinition(
        name="yolo",
        display_name="YOLO & Object Detection",
        description="Object detection inference, bounding box utilities, annotation formats",
        applicable_languages=[Language.PYTHON],
        subdomains=[
            SubDomain(name="inference", description="Load model, run detection, parse results"),
            SubDomain(name="bbox", description="Box format conversion, IoU, NMS, crop"),
            SubDomain(name="annotation", description="COCO, YOLO txt, Pascal VOC parsing"),
        ],
        complexity_hints={
            Complexity.BASIC: [
                "load YOLO pretrained model (ultralytics)",
                "run inference on single image",
                "parse detections (class, confidence, bbox)",
                "draw bounding boxes with labels",
                "bbox format: xyxy to xywh conversion",
                "bbox format: xywh to xyxy conversion",
                "IoU (Intersection over Union) calculation",
            ],
            Complexity.MEDIUM: [
                "run YOLO on video stream",
                "filter detections by confidence threshold",
                "filter detections by class name",
                "NMS (non-max suppression) from scratch",
                "crop detected regions from image",
                "normalized to pixel coordinates conversion",
                "parse COCO JSON annotations",
                "parse YOLO txt format annotations",
            ],
            Complexity.ADVANCED: [
                "custom dataset YAML for YOLO training",
                "fine-tune YOLO on custom classes",
                "export model to ONNX",
                "convert between COCO, YOLO, Pascal VOC formats",
                "batch inference with result aggregation",
                "train/val split for image datasets",
            ],
        },
        estimated_snippets=25,
    ),
    # ──────────────────────────────────────────────────
    # LLM SDKs
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="llm_sdks",
        display_name="LLM API SDKs",
        description="OpenAI, Gemini, Anthropic SDK patterns for quick prototyping",
        applicable_languages=[Language.PYTHON],
        subdomains=[
            SubDomain(name="openai", description="OpenAI chat completions, tools, embeddings"),
            SubDomain(name="gemini", description="Google Gemini generate, multimodal, tools"),
            SubDomain(name="anthropic", description="Anthropic messages, tools, streaming"),
            SubDomain(name="common", description="Retry, rate limit, prompt template, RAG"),
        ],
        complexity_hints={
            Complexity.BASIC: [
                "OpenAI client setup and simple chat completion",
                "Gemini client setup and generate_content",
                "Anthropic client setup and messages.create",
                "set temperature, max_tokens, system prompt",
                "streaming response to stdout",
            ],
            Complexity.MEDIUM: [
                "multi-turn conversation with history",
                "function calling / tool use (OpenAI)",
                "function calling / tool use (Gemini)",
                "tool use (Anthropic)",
                "vision: send image + text prompt",
                "embeddings API call (OpenAI)",
                "JSON mode / structured output",
            ],
            Complexity.ADVANCED: [
                "async batch calls to LLM",
                "retry with exponential backoff wrapper",
                "rate limiter for API calls",
                "simple RAG: embed query → search → stuff context → call LLM",
                "prompt template builder with variable substitution",
                "cost estimator by token count",
                "streaming with tool use",
            ],
        },
        estimated_snippets=30,
    ),
    # ──────────────────────────────────────────────────
    # SHELL / SSH / LINUX
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="bash_scripting",
        display_name="Bash Scripting",
        description="Shell scripting primitives for automation",
        applicable_languages=[Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "script template with set -euo pipefail",
                "variables, loops (for, while), conditionals",
                "read user input",
                "file existence checks (-f, -d, -e)",
                "string comparison in bash",
                "array declaration and iteration",
            ],
            Complexity.MEDIUM: [
                "pipe and process substitution",
                "sed find and replace in file",
                "awk column extraction and filtering",
                "getopts argument parsing",
                "trap for cleanup on exit",
                "here document",
                "color output in terminal",
                "check if command exists",
            ],
            Complexity.ADVANCED: [
                "parallel execution with xargs",
                "log function with timestamps",
                "lock file to prevent duplicate runs",
                "background process management",
                "automatic retry wrapper function",
                "SSH remote command execution in script",
            ],
        },
        estimated_snippets=20,
    ),
    DomainDefinition(
        name="ssh_linux",
        display_name="SSH & Linux Commands",
        description="System administration, SSH operations, Linux utilities",
        applicable_languages=[Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "SSH connect to remote host",
                "SCP file copy to/from remote",
                "file permissions (chmod, chown)",
                "disk usage (df, du)",
                "process list (ps, top, htop)",
                "find files by name, size, date",
                "tar compress and extract",
            ],
            Complexity.MEDIUM: [
                "SSH key generation and setup",
                "SSH config file for multiple hosts",
                "systemctl start/stop/status/enable",
                "journalctl log viewing with filters",
                "netstat / ss for port checking",
                "user and group management",
                "cron job setup and common schedules",
                "rsync for efficient file sync",
            ],
            Complexity.ADVANCED: [
                "SSH tunneling (local and remote port forward)",
                "SSH jump host / bastion pattern",
                "iptables / ufw firewall rules",
                "strace / lsof for debugging",
                "process resource limits (ulimit)",
                "disk partitioning and mounting",
                "systemd service file creation",
            ],
        },
        estimated_snippets=25,
    ),
    # ──────────────────────────────────────────────────
    # PYTHON STDLIB NICHE
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="python_stdlib",
        display_name="Python Standard Library Patterns",
        description="contextlib, functools, itertools, collections, pathlib — the niche but essential stdlib",
        applicable_languages=[Language.PYTHON],
        subdomains=[
            SubDomain(name="contextlib", description="Context managers, suppress, ExitStack"),
            SubDomain(name="functools", description="lru_cache, partial, wraps, reduce"),
            SubDomain(name="itertools", description="chain, product, groupby, islice"),
            SubDomain(name="collections", description="defaultdict, Counter, deque, namedtuple"),
            SubDomain(name="pathlib", description="Path operations, glob, read/write"),
        ],
        complexity_hints={
            Complexity.BASIC: [
                "pathlib Path: read_text, write_text, mkdir, glob, exists",
                "collections.Counter most_common",
                "collections.defaultdict with list/int",
                "functools.lru_cache decorator",
                "itertools.chain to flatten iterables",
            ],
            Complexity.MEDIUM: [
                "contextlib.contextmanager custom context manager",
                "contextlib.suppress specific exceptions",
                "functools.partial for pre-filling arguments",
                "functools.wraps for decorator metadata",
                "itertools.product for cartesian product",
                "itertools.groupby with key function",
                "collections.deque as fixed-size buffer",
                "functools.cached_property",
            ],
            Complexity.ADVANCED: [
                "contextlib.ExitStack for dynamic context management",
                "functools.singledispatch for function overloading",
                "functools.reduce for cumulative operations",
                "itertools recipes: pairwise, chunked, flatten",
                "collections.ChainMap for layered config",
                "functools.total_ordering for comparison methods",
            ],
        },
        estimated_snippets=25,
    ),
    # ──────────────────────────────────────────────────
    # PYDANTIC
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="pydantic",
        display_name="Pydantic & Data Models",
        description="Pydantic v2 models, validators, enums, settings, serialization",
        applicable_languages=[Language.PYTHON],
        complexity_hints={
            Complexity.BASIC: [
                "simple BaseModel with typed fields",
                "optional fields and default values",
                "model_dump and model_json_schema",
                "basic Enum and StrEnum definition",
                "model instance creation and validation",
            ],
            Complexity.MEDIUM: [
                "field_validator for custom validation",
                "model_validator (before/after)",
                "nested models",
                "Literal types and discriminated unions",
                "alias fields and model_config",
                "computed_field",
                "JSON serialization/deserialization",
            ],
            Complexity.ADVANCED: [
                "generic models with TypeVar",
                "dynamic model creation with create_model",
                "BaseSettings with .env file loading",
                "custom JSON encoders",
                "complex enum with values and methods",
                "model inheritance patterns",
            ],
        },
        estimated_snippets=20,
    ),
    # ──────────────────────────────────────────────────
    # FRONTEND
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="frontend",
        display_name="Frontend — HTML/CSS/JS",
        description="Web frontend primitives from static pages to interactive dashboards",
        applicable_languages=[Language.HTML, Language.JAVASCRIPT],
        complexity_hints={
            Complexity.BASIC: [
                "HTML5 boilerplate with meta tags",
                "responsive CSS grid layout",
                "form with input validation",
                "DOM manipulation (querySelector, addEventListener)",
                "fetch API GET and POST request",
                "local storage read/write",
            ],
            Complexity.MEDIUM: [
                "dynamic table from JSON data",
                "tab/panel switcher component",
                "modal dialog component",
                "debounce and throttle functions",
                "infinite scroll pattern",
                "dark mode toggle with CSS variables",
                "drag and drop sortable list",
            ],
            Complexity.ADVANCED: [
                "SPA router (hash-based)",
                "state management pattern (pub/sub)",
                "WebSocket connection with reconnect",
                "dashboard layout with switchable panels",
                "real-time data update with SSE",
                "virtual scroll for large lists",
            ],
        },
        estimated_snippets=20,
    ),
    # ──────────────────────────────────────────────────
    # GIT / DOCKER / CONFIG / TESTING / etc.
    # ──────────────────────────────────────────────────
    DomainDefinition(
        name="git",
        display_name="Git Version Control",
        description="Git commands and workflows every developer uses",
        applicable_languages=[Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "clone, init, add, commit, push, pull",
                "branch create, switch, list, delete",
                "git status, log (oneline, graph), diff",
                "gitignore patterns for Python, C++, Node",
            ],
            Complexity.MEDIUM: [
                "merge and resolve conflicts",
                "rebase interactive",
                "cherry-pick specific commits",
                "stash save, pop, list, apply",
                "git log search by message, author, date",
                "undo last commit (soft, mixed, hard reset)",
            ],
            Complexity.ADVANCED: [
                "git bisect to find bug introduction",
                "reflog to recover lost commits",
                "submodule add, update, sync",
                "git hooks (pre-commit, pre-push)",
                "squash commits before merge",
                "worktree for parallel branches",
            ],
        },
        estimated_snippets=20,
    ),
    DomainDefinition(
        name="docker",
        display_name="Docker & Containers",
        description="Dockerfile, compose, and container management patterns",
        applicable_languages=[Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "Python app Dockerfile",
                "docker build, run, stop, rm, logs",
                "port mapping and volume mount",
                "docker-compose basic (app + db)",
                "environment variables in compose",
            ],
            Complexity.MEDIUM: [
                "multi-stage build for smaller images",
                "docker-compose with multiple services (app + postgres + redis)",
                "healthcheck in Dockerfile and compose",
                "networking between containers",
                ".dockerignore file",
                "entrypoint script pattern",
            ],
            Complexity.ADVANCED: [
                "image size optimization techniques",
                "compose profiles for dev/prod",
                "docker build cache optimization",
                "non-root user in container",
                "docker exec and debug running container",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="testing",
        display_name="Testing — Pytest",
        description="Unit testing, mocking, fixtures, parameterized tests",
        applicable_languages=[Language.PYTHON],
        complexity_hints={
            Complexity.BASIC: [
                "basic test function with assert",
                "test class organization",
                "pytest.raises for exception testing",
                "simple fixture",
                "run tests with pytest CLI flags",
            ],
            Complexity.MEDIUM: [
                "parametrize decorator for multiple inputs",
                "fixtures with setup/teardown (yield)",
                "mock.patch for external dependencies",
                "mock return_value and side_effect",
                "conftest.py shared fixtures",
                "tmp_path fixture for file tests",
            ],
            Complexity.ADVANCED: [
                "async test with pytest-asyncio",
                "coverage configuration and reporting",
                "custom markers and filtering",
                "factory fixture pattern",
                "monkeypatch for env vars and attributes",
                "integration test with test database",
            ],
        },
        estimated_snippets=20,
    ),
    DomainDefinition(
        name="error_handling",
        display_name="Error Handling & Debugging",
        description="Try/catch patterns, custom exceptions, logging, debugging techniques",
        applicable_languages=[Language.PYTHON, Language.CPP, Language.JAVASCRIPT],
        complexity_hints={
            Complexity.BASIC: [
                "try/except/finally basic pattern",
                "catch specific exception types",
                "raise custom exception",
                "basic logging setup (logging.basicConfig)",
                "print debugging with repr",
            ],
            Complexity.MEDIUM: [
                "custom exception hierarchy",
                "exception chaining (raise from)",
                "logging with file handler and rotation",
                "structured logging as JSON",
                "assertions for invariants",
                "traceback.format_exc for error reporting",
            ],
            Complexity.ADVANCED: [
                "context manager for error suppression and logging",
                "retry decorator with exception filtering",
                "global exception handler",
                "memory debugging with tracemalloc (Python)",
                "core dump analysis basics (C++)",
                "profiling with cProfile / timeit",
            ],
        },
        estimated_snippets=20,
    ),
    DomainDefinition(
        name="security",
        display_name="Security Primitives",
        description="Hashing, encryption, JWT, password handling, cert management",
        applicable_languages=[Language.PYTHON, Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "hash a string with SHA256",
                "password hash with bcrypt",
                "password verify with bcrypt",
                "generate random token (secrets module)",
                "generate UUID",
            ],
            Complexity.MEDIUM: [
                "JWT encode and decode",
                "symmetric encryption with Fernet",
                "HMAC signature generation and verification",
                "API key validation pattern",
                "hash file for integrity check (MD5, SHA256)",
            ],
            Complexity.ADVANCED: [
                "RSA key pair generation",
                "asymmetric encrypt/decrypt",
                "SSL certificate info extraction",
                "secure password generator with policy",
                "constant-time string comparison",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="serialization",
        display_name="Serialization & Data Formats",
        description="JSON, CSV, YAML, TOML, protobuf, XML — read, write, convert",
        applicable_languages=[Language.PYTHON, Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "JSON read from file and write to file",
                "JSON pretty print",
                "CSV read and write with csv module",
                "YAML safe_load and dump",
                "TOML parsing (tomllib)",
            ],
            Complexity.MEDIUM: [
                "custom JSON encoder for datetime, Decimal, etc",
                "CSV DictReader and DictWriter",
                "XML parsing with ElementTree",
                "convert between JSON, YAML, TOML",
                "pickle serialize and deserialize (with warning)",
            ],
            Complexity.ADVANCED: [
                "JSON schema validation",
                "streaming JSON parsing for large files",
                "binary struct pack/unpack",
                "protobuf definition and Python usage",
                "data versioning pattern for schema changes",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="networking",
        display_name="Networking & HTTP",
        description="HTTP calls, sockets, downloads, API patterns",
        applicable_languages=[Language.PYTHON, Language.BASH, Language.JAVASCRIPT],
        complexity_hints={
            Complexity.BASIC: [
                "HTTP GET with requests library",
                "HTTP POST with JSON body",
                "download file with progress",
                "curl equivalent commands (bash)",
                "fetch API GET and POST (JavaScript)",
            ],
            Complexity.MEDIUM: [
                "requests session with headers and cookies",
                "async HTTP with aiohttp",
                "TCP socket server and client",
                "UDP send and receive",
                "check if port is open",
                "URL parsing and construction",
            ],
            Complexity.ADVANCED: [
                "WebSocket client",
                "simple HTTP server (stdlib)",
                "connection pooling with requests.Session",
                "retry and timeout configuration",
                "multipart file upload",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="webscraping",
        display_name="Web Scraping",
        description="BeautifulSoup, Selenium, async scraping patterns",
        applicable_languages=[Language.PYTHON],
        complexity_hints={
            Complexity.BASIC: [
                "requests + BeautifulSoup: fetch and parse page",
                "find elements by tag, class, id",
                "extract text, attributes, links from elements",
                "save scraped data to CSV",
            ],
            Complexity.MEDIUM: [
                "handle pagination (next page loop)",
                "set headers and user agent",
                "handle cookies and sessions",
                "Selenium: open browser, navigate, click, type",
                "Selenium: wait for element",
            ],
            Complexity.ADVANCED: [
                "async scraping with aiohttp + BeautifulSoup",
                "rate limiting between requests",
                "proxy rotation pattern",
                "extract structured data (tables) from HTML",
                "handle JavaScript-rendered pages with Selenium",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="fastapi",
        display_name="API Development — FastAPI",
        description="FastAPI route, middleware, auth, WebSocket patterns",
        applicable_languages=[Language.PYTHON],
        complexity_hints={
            Complexity.BASIC: [
                "FastAPI hello world with uvicorn",
                "route with path and query parameters",
                "request body with Pydantic model",
                "response model and status codes",
                "CORS middleware setup",
            ],
            Complexity.MEDIUM: [
                "dependency injection pattern",
                "file upload endpoint",
                "background task",
                "WebSocket endpoint",
                "error handling with HTTPException",
                "router organization with APIRouter",
            ],
            Complexity.ADVANCED: [
                "auth middleware (JWT bearer)",
                "rate limiting middleware",
                "database session dependency",
                "streaming response",
                "lifespan events (startup/shutdown)",
                "custom OpenAPI schema",
            ],
        },
        estimated_snippets=20,
    ),
    DomainDefinition(
        name="deep_learning",
        display_name="Deep Learning — PyTorch",
        description="PyTorch training loops, model definitions, data loading",
        applicable_languages=[Language.PYTHON],
        complexity_hints={
            Complexity.BASIC: [
                "tensor creation and basic operations",
                "simple Sequential model",
                "loss function and optimizer setup",
                "basic training loop boilerplate",
                "GPU device handling (cuda/mps/cpu)",
                "save and load model weights",
            ],
            Complexity.MEDIUM: [
                "custom Dataset class",
                "DataLoader with batching and shuffling",
                "CNN template (Conv2d, MaxPool, FC layers)",
                "training + validation loop with metrics",
                "learning rate scheduler",
                "TensorBoard logging basics",
            ],
            Complexity.ADVANCED: [
                "transfer learning with pretrained model",
                "custom loss function",
                "early stopping implementation",
                "gradient clipping",
                "mixed precision training (autocast + GradScaler)",
                "model export to ONNX",
            ],
        },
        estimated_snippets=20,
    ),
    DomainDefinition(
        name="visualization",
        display_name="Data Visualization",
        description="Matplotlib, Seaborn, Plotly charting patterns",
        applicable_languages=[Language.PYTHON],
        complexity_hints={
            Complexity.BASIC: [
                "matplotlib line plot",
                "matplotlib bar chart",
                "matplotlib scatter plot",
                "plt.savefig and display boilerplate",
                "pandas .plot() shortcut",
            ],
            Complexity.MEDIUM: [
                "subplots grid layout",
                "seaborn heatmap",
                "seaborn distribution plots (histplot, kdeplot)",
                "seaborn pairplot",
                "annotate points on chart",
                "dual y-axis plot",
            ],
            Complexity.ADVANCED: [
                "plotly interactive line/bar chart",
                "custom matplotlib style and theme",
                "animation with FuncAnimation",
                "3D plot with mpl_toolkits",
                "dashboard-style multi-chart figure",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="datetime",
        display_name="Date & Time Operations",
        description="Datetime manipulation, timezone handling, formatting, duration math",
        applicable_languages=[Language.PYTHON, Language.JAVASCRIPT, Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "get current datetime",
                "format datetime to string (strftime)",
                "parse string to datetime (strptime)",
                "date arithmetic (add/subtract days)",
                "epoch timestamp to datetime and back",
            ],
            Complexity.MEDIUM: [
                "timezone conversion (pytz / zoneinfo)",
                "calculate time difference / duration",
                "date range generation",
                "first/last day of month/week",
                "ISO 8601 format handling",
                "human-readable relative time (2 hours ago)",
            ],
            Complexity.ADVANCED: [
                "recurring date pattern (every Nth weekday)",
                "business days calculation",
                "overlap detection between date ranges",
                "timezone-aware datetime comparison",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="concurrency",
        display_name="Concurrency & Parallelism",
        description="Threads, processes, async/await, locks, pools",
        applicable_languages=[Language.PYTHON, Language.CPP],
        complexity_hints={
            Complexity.BASIC: [
                "threading.Thread basic usage",
                "concurrent.futures.ThreadPoolExecutor",
                "concurrent.futures.ProcessPoolExecutor",
                "asyncio basic async/await pattern",
                "asyncio.gather for parallel tasks",
            ],
            Complexity.MEDIUM: [
                "threading Lock for shared state",
                "asyncio.Semaphore for rate limiting",
                "asyncio.Queue producer/consumer",
                "multiprocessing with shared memory",
                "thread-safe counter",
                "async context manager",
            ],
            Complexity.ADVANCED: [
                "asyncio.TaskGroup (Python 3.11+)",
                "reader-writer lock pattern",
                "async generator / async iterator",
                "graceful shutdown with signal handling",
                "C++ std::thread and std::mutex",
                "C++ std::async and std::future",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="cloud_aws",
        display_name="Cloud & AWS (boto3 / CLI)",
        description="AWS service interactions via CLI and Python SDK",
        applicable_languages=[Language.PYTHON, Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "boto3 S3: upload, download, list objects",
                "aws s3 cp, ls, sync (CLI)",
                "boto3 session and client setup",
                "environment variable AWS credentials",
            ],
            Complexity.MEDIUM: [
                "S3 presigned URL generation",
                "SQS send and receive messages",
                "DynamoDB put_item, get_item, query",
                "Lambda invoke from Python",
                "EC2 describe instances",
                "SSM parameter store get/put",
            ],
            Complexity.ADVANCED: [
                "S3 multipart upload for large files",
                "SQS dead letter queue pattern",
                "DynamoDB batch write and scan with pagination",
                "CloudWatch put custom metrics",
                "assume role with STS",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="env_config",
        display_name="Environment & Configuration",
        description="Env vars, config files, CLI args, secrets management",
        applicable_languages=[Language.PYTHON, Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "read environment variables with defaults",
                "python-dotenv .env file loading",
                "argparse basic CLI argument parsing",
                "JSON config file loading",
            ],
            Complexity.MEDIUM: [
                "argparse with subcommands",
                "YAML config with nested structure",
                "Pydantic BaseSettings with .env",
                "typer/click CLI framework basics",
                "config validation and type coercion",
            ],
            Complexity.ADVANCED: [
                "layered config: defaults < file < env < CLI",
                "feature flags implementation",
                "dynamic config reload without restart",
                "secrets from environment with masking",
            ],
        },
        estimated_snippets=12,
    ),
    DomainDefinition(
        name="file_io",
        display_name="File I/O & Filesystem",
        description="Read, write, copy, move, watch files and directories",
        applicable_languages=[Language.PYTHON, Language.CPP, Language.BASH],
        complexity_hints={
            Complexity.BASIC: [
                "read text file (pathlib)",
                "write text file (pathlib)",
                "read/write binary file",
                "list files in directory (glob)",
                "check if file/directory exists",
                "create directory with parents",
            ],
            Complexity.MEDIUM: [
                "copy and move files (shutil)",
                "temporary file and directory (tempfile)",
                "read file line by line (memory efficient)",
                "file locking pattern",
                "walk directory tree recursively",
                "watch directory for changes",
                "PDF reading (pdfplumber/PyPDF2)",
                "Excel read/write (openpyxl)",
            ],
            Complexity.ADVANCED: [
                "atomic file write (write to tmp, then rename)",
                "memory-mapped file I/O",
                "zip/unzip files programmatically",
                "tar.gz compress and extract",
                "file checksum (MD5/SHA256)",
                "C++ fstream read/write patterns",
            ],
        },
        estimated_snippets=20,
    ),
    DomainDefinition(
        name="numbers_math",
        display_name="Numbers & Math Operations",
        description="Numeric operations, precision math, random, bit manipulation",
        applicable_languages=[Language.PYTHON, Language.CPP, Language.JAVASCRIPT],
        complexity_hints={
            Complexity.BASIC: [
                "integer division, modulo, power",
                "float rounding (round, ceil, floor)",
                "min, max, sum, abs",
                "random number generation (int, float, choice)",
                "number to string formatting (decimal places, commas)",
            ],
            Complexity.MEDIUM: [
                "decimal module for precise arithmetic",
                "statistics (mean, median, std dev)",
                "clamp value to range",
                "greatest common divisor and least common multiple",
                "percentage calculation and change",
                "random shuffle, sample, weighted choice",
            ],
            Complexity.ADVANCED: [
                "bit manipulation (set, clear, toggle, check bit)",
                "binary/hex/octal conversion",
                "matrix operations without numpy",
                "prime number check and sieve",
                "C++ numeric_limits and overflow detection",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="regex",
        display_name="Regular Expressions",
        description="Regex patterns used across strings, files, shell, and data processing",
        applicable_languages=[Language.PYTHON, Language.BASH, Language.JAVASCRIPT],
        complexity_hints={
            Complexity.BASIC: [
                "match exact string",
                "search for pattern in text",
                "findall occurrences",
                "substitute / replace pattern",
                "compile regex for reuse",
                "common patterns: email, URL, phone, IP address",
            ],
            Complexity.MEDIUM: [
                "capture groups and named groups",
                "non-greedy matching",
                "lookahead and lookbehind",
                "split by regex pattern",
                "multiline and dotall flags",
                "extract all matches with groups",
            ],
            Complexity.ADVANCED: [
                "complex validation pattern (password rules)",
                "regex substitution with function callback",
                "parse structured text (log lines, CSV-like)",
                "grep/sed/awk regex in bash",
                "performance: avoid catastrophic backtracking",
            ],
        },
        estimated_snippets=15,
    ),
    DomainDefinition(
        name="numpy",
        display_name="NumPy Operations",
        description="Array operations, linear algebra, random, vectorized computation",
        applicable_languages=[Language.PYTHON],
        complexity_hints={
            Complexity.BASIC: [
                "array creation (zeros, ones, arange, linspace)",
                "reshape and flatten",
                "basic slicing and indexing",
                "element-wise math operations",
                "random array generation",
            ],
            Complexity.MEDIUM: [
                "broadcasting rules and examples",
                "vectorized operations vs loops",
                "dot product and matrix multiply",
                "np.where conditional selection",
                "sorting and argsort",
                "unique values and counts",
            ],
            Complexity.ADVANCED: [
                "fancy indexing (boolean and integer)",
                "einsum for complex tensor ops",
                "structured arrays / record arrays",
                "save/load arrays (npz, npy)",
                "memory layout (C vs Fortran order)",
            ],
        },
        estimated_snippets=15,
    ),
]


def get_all_domains() -> list[DomainDefinition]:
    return DOMAINS


def get_domain_by_name(name: str) -> DomainDefinition | None:
    for d in DOMAINS:
        if d.name == name:
            return d
    return None


def get_all_tasks() -> list[dict]:
    """Explode all domains into individual generation tasks."""
    tasks = []
    for domain in DOMAINS:
        tasks.extend(domain.get_generation_tasks())
    return tasks


def print_domain_summary():
    total_snippets = sum(d.estimated_snippets for d in DOMAINS)
    total_tasks = sum(len(d.get_generation_tasks()) for d in DOMAINS)
    print(f"\nDomains: {len(DOMAINS)}")
    print(f"Estimated snippets: {total_snippets}")
    print(f"Generation tasks: {total_tasks}")
    print()
    for d in DOMAINS:
        langs = ", ".join(l.value for l in d.applicable_languages)
        tasks = len(d.get_generation_tasks())
        print(f"  {d.name:20s} | {langs:30s} | ~{d.estimated_snippets:3d} snippets | {tasks} tasks")