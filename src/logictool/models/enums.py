from enum import StrEnum


class Language(StrEnum):
    PYTHON = "python"
    CPP = "cpp"
    BASH = "bash"
    JAVASCRIPT = "javascript"
    HTML = "html"


class Complexity(StrEnum):
    BASIC = "basic"
    MEDIUM = "medium"
    ADVANCED = "advanced"


class SnippetType(StrEnum):
    SNIPPET = "snippet"        # Small atomic logic (3-30 lines)
    BOILERPLATE = "boilerplate" # Full file skeleton (30-150 lines)


class LLMProvider(StrEnum):
    CLAUDE = "claude"
    GEMINI = "gemini"