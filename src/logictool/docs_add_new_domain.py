"""
HOW TO ADD A NEW DOMAIN TO LOGICTOOL
=====================================

1. Open: src/logictool/config/domains.py
2. Add a new DomainDefinition to the DOMAINS list (see template below)
3. Run: uv run logictool domains          (verify it shows up)
4. Run: uv run logictool generate --provider claude --domain your_domain
5. Run: uv run logictool import            (import new JSON into SQLite)
6. Run: uv run logictool rebuild-index     (update semantic search vectors)
7. Run: uv run logictool search "your query"  (test it)

That's it. No other files need to change.
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEMPLATE — Copy this, fill in, paste into DOMAINS list
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from logictool.models.domain import DomainDefinition, SubDomain
from logictool.models.enums import Complexity, Language

TEMPLATE = DomainDefinition(
    # REQUIRED: unique identifier (lowercase, underscores, no spaces)
    name="your_domain",

    # REQUIRED: human-readable name shown in CLI output
    display_name="Your Domain Name",

    # REQUIRED: tells the LLM what this domain is about
    description="One or two sentences describing what snippets to generate",

    # REQUIRED: which languages to generate for
    # Pick from: Language.PYTHON, Language.CPP, Language.BASH,
    #            Language.JAVASCRIPT, Language.HTML
    applicable_languages=[Language.PYTHON],

    # OPTIONAL: break domain into sub-areas for better organization
    subdomains=[
        SubDomain(
            name="subarea_one",
            description="What this sub-area covers",
            example_topics=["topic1", "topic2"],
        ),
        SubDomain(
            name="subarea_two",
            description="Another sub-area",
        ),
    ],

    # REQUIRED: what to generate at each complexity level
    # These hints are sent directly to the LLM as generation instructions
    # Be specific — the more detail, the better the snippets
    complexity_hints={
        Complexity.BASIC: [
            "simple thing every developer does",
            "another basic pattern",
            "one more common operation",
        ],
        Complexity.MEDIUM: [
            "intermediate pattern that needs some thought",
            "another medium complexity task",
        ],
        Complexity.ADVANCED: [
            "complex pattern used in production",
            "advanced technique most devs look up",
        ],
    },

    # OPTIONAL: rough estimate for stats display
    estimated_snippets=20,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REAL EXAMPLES — Domains you might want to add
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ─── Example 1: Kafka / Message Queues ───────────
example_kafka = DomainDefinition(
    name="kafka",
    display_name="Kafka & Message Queues",
    description="Kafka producer/consumer patterns, message serialization, topic management",
    applicable_languages=[Language.PYTHON],
    subdomains=[
        SubDomain(name="producer", description="Send messages to topics"),
        SubDomain(name="consumer", description="Read messages, consumer groups"),
        SubDomain(name="admin", description="Topic creation, partition management"),
    ],
    complexity_hints={
        Complexity.BASIC: [
            "KafkaProducer setup and send message",
            "KafkaConsumer setup and read messages",
            "JSON serializer/deserializer for messages",
            "connect to Kafka broker with bootstrap servers",
        ],
        Complexity.MEDIUM: [
            "consumer group with auto offset commit",
            "producer with acknowledgment and retries",
            "Avro schema serialization",
            "topic creation with AdminClient",
            "consumer with manual offset commit",
        ],
        Complexity.ADVANCED: [
            "exactly-once semantics with transactions",
            "dead letter queue pattern",
            "consumer rebalance listener",
            "batch producer with compression",
            "partition assignment strategy",
        ],
    },
    estimated_snippets=15,
)

# ─── Example 2: GraphQL ─────────────────────────
example_graphql = DomainDefinition(
    name="graphql",
    display_name="GraphQL (Strawberry / Apollo)",
    description="GraphQL schema definition, queries, mutations, resolvers",
    applicable_languages=[Language.PYTHON, Language.JAVASCRIPT],
    complexity_hints={
        Complexity.BASIC: [
            "define a simple type and query (Strawberry for Python)",
            "query with arguments",
            "mutation for creating a resource",
            "Apollo Client setup and simple query (JS)",
        ],
        Complexity.MEDIUM: [
            "nested types and relationships",
            "input types for mutations",
            "pagination (cursor-based)",
            "error handling in resolvers",
            "DataLoader for N+1 problem",
        ],
        Complexity.ADVANCED: [
            "subscriptions (real-time)",
            "custom scalar types",
            "authentication in resolvers",
            "file upload via GraphQL",
            "schema stitching / federation basics",
        ],
    },
    estimated_snippets=15,
)

# ─── Example 3: Terraform / IaC ─────────────────
example_terraform = DomainDefinition(
    name="terraform",
    display_name="Terraform & IaC",
    description="Infrastructure as code patterns for cloud resource management",
    applicable_languages=[Language.BASH],  # HCL via bash context
    complexity_hints={
        Complexity.BASIC: [
            "provider and backend configuration",
            "define EC2 instance resource",
            "define S3 bucket resource",
            "variables and outputs",
            "terraform init, plan, apply commands",
        ],
        Complexity.MEDIUM: [
            "modules for reusable infrastructure",
            "data sources to reference existing resources",
            "count and for_each for multiple resources",
            "remote state with S3 backend",
            "locals for computed values",
        ],
        Complexity.ADVANCED: [
            "dynamic blocks",
            "workspace management for environments",
            "import existing infrastructure",
            "state manipulation (move, remove)",
            "custom validation rules on variables",
        ],
    },
    estimated_snippets=15,
)

# ─── Example 4: Rust (if you add a new language) ─
# First add to enums.py:
#   class Language(StrEnum):
#       RUST = "rust"
#
# Then add the domain:

# example_rust = DomainDefinition(
#     name="rust_basics",
#     display_name="Rust Fundamentals",
#     description="Rust ownership, borrowing, error handling, common patterns",
#     applicable_languages=[Language.RUST],
#     complexity_hints={
#         Complexity.BASIC: [
#             "variable binding and mutability",
#             "string types (String vs &str)",
#             "Vec operations (push, iter, map, filter)",
#             "Result and Option handling",
#             "struct definition with impl",
#         ],
#         Complexity.MEDIUM: [...],
#         Complexity.ADVANCED: [...],
#     },
# )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDING A NEW LANGUAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 1. Add to src/logictool/models/enums.py:
#
#      class Language(StrEnum):
#          PYTHON = "python"
#          CPP = "cpp"
#          ...
#          RUST = "rust"       # ← add here
#          GO = "go"           # ← or here
#
# 2. Update the LANG_MAP in src/logictool/cli/display.py
#    for syntax highlighting:
#
#      LANG_MAP = {
#          "python": "python",
#          ...
#          "rust": "rust",
#          "go": "go",
#      }
#
# 3. Create your domain definition as shown above
# 4. Generate, import, rebuild-index, search


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPLETE WORKFLOW AFTER ADDING A DOMAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Terminal commands:
#
#   # 1. Verify domain shows up
#   uv run logictool domains
#
#   # 2. Generate snippets for ONLY the new domain
#   uv run logictool generate --provider claude --domain kafka
#
#   # 3. Import new snippets into database
#   uv run logictool import
#
#   # 4. Rebuild semantic search index (adds new embeddings)
#   uv run logictool rebuild-index
#
#   # 5. Test search
#   uv run logictool search "kafka consumer group"
#   uv run logictool browse --domain kafka
#   uv run logictool stats
