"""Unofficial OpenAI-compatible client for chat.deepseek.com."""

# Load .env before importing submodules that read configuration at import time.
from dotenv import load_dotenv

load_dotenv()

from .auth import Session, get_session, login
from .client import DeepSeekClient, Reply
from .pow import DeepSeekPow

__all__ = ["Session", "get_session", "login", "DeepSeekClient", "Reply", "DeepSeekPow"]
