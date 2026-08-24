"""Wires up the (in-memory, fake) model clients, cache, and service shared
across routers. There's no database or DI framework here, so this module
just owns the singleton instances every route depends on.
"""

from app.cache.response_cache import ResponseCache
from app.clients.fake_model_client import FakeModelClient
from app.services.llm_router_service import LLMRouterService

primary_client = FakeModelClient(name="primary-model")
fallback_client = FakeModelClient(name="fallback-model")
response_cache = ResponseCache()

llm_router_service = LLMRouterService(primary_client, fallback_client, response_cache)
