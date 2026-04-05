SYSTEM_PROMPT = """You are a senior developer creating a curated library of code snippets.
Your goal is to produce PRODUCTION-READY, COPY-PASTE-READY code primitives.

RULES:
1. Every snippet must be self-contained and immediately runnable.
2. Use modern syntax and best practices for the given language.
3. Include necessary imports at the top of each snippet.
4. No placeholder comments like "# your code here" — give complete working code.
5. Keep snippets focused on ONE task. No kitchen-sink functions.
6. For Python: use type hints, f-strings, pathlib over os.path.
7. For C++: use modern C++ (17/20 features where appropriate).
8. For Bash: use shellcheck-clean syntax, set -euo pipefail where relevant.
9. For JavaScript: use ES6+, const/let, arrow functions, async/await.

OUTPUT FORMAT:
Respond with ONLY a valid JSON array. No markdown, no backticks, no explanation.
Each element must have exactly these fields:
{
    "title": "short descriptive name",
    "description": "what this snippet does and when to use it",
    "code": "the actual code as a string (use \\n for newlines)",
    "why": "one-line explanation of WHY this approach works",
    "tags": ["tag1", "tag2", "tag3"],
    "subdomain": "specific area or null"
}
"""


def build_generation_prompt(
    domain: str,
    display_name: str,
    description: str,
    language: str,
    complexity: str,
    hints: list[str],
    subdomains: list[dict] | None = None,
) -> str:
    hints_str = "\n".join(f"  - {h}" for h in hints)

    subdomain_str = ""
    if subdomains:
        subdomain_str = "\n\nSubdomains to cover:\n"
        for sd in subdomains:
            topics = ", ".join(sd.get("example_topics", []))
            subdomain_str += f"  - {sd['name']}: {sd['description']}"
            if topics:
                subdomain_str += f" (topics: {topics})"
            subdomain_str += "\n"

    return f"""Generate {complexity.upper()} level code snippets for the domain: {display_name}

Domain description: {description}
Language: {language}
Complexity level: {complexity}

Topics to cover at this level:
{hints_str}
{subdomain_str}
Generate between 5-10 snippets that cover the above topics comprehensively.
Each snippet should be a distinct, reusable primitive — not variations of the same thing.

Remember: Output ONLY a valid JSON array. No markdown fences, no preamble."""