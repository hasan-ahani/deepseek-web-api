"""Unofficial OpenAI-compatible client for chat.deepseek.com."""

import importlib

# Load .env before importing submodules that read configuration at import time.
from dotenv import load_dotenv

load_dotenv()

__all__ = ["Session", "get_session", "login", "DeepSeekClient", "Reply", "DeepSeekPow"]

# Attribute -> submodule it lives in. Resolved lazily so that running
# `python -m deepseek.auth` does not import `deepseek.auth` at package-import
# time (which makes runpy warn about a module found in sys.modules).
_SUBMODULES = {
    "Session": "auth",
    "get_session": "auth",
    "login": "auth",
    "DeepSeekClient": "client",
    "Reply": "client",
    "DeepSeekPow": "pow",
}


def __getattr__(name: str):
    submodule = _SUBMODULES.get(name)
    if submodule is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    return getattr(importlib.import_module(f".{submodule}", __name__), name)
