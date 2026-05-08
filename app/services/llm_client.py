from typing import Optional

from openai import AsyncOpenAI

from app.config import settings

_client: Optional[AsyncOpenAI] = None


class LLMServiceError(Exception):
    pass


def get_client() -> AsyncOpenAI:
    global _client
    if not settings.OPENAI_API_KEY:
        raise LLMServiceError("OPENAI_API_KEY is not configured")
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client
