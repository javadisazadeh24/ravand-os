"""
RAVAND OS – AI Service
Production-grade service class for communicating with a local Ollama server.

Architecture notes:
  • Stateless – instantiate once and reuse (singleton via dependency injection).
  • All I/O is synchronous (requests library).
    For async support in the future, swap to httpx with AsyncClient.
  • Multi-model capable – every public method accepts an optional model override.
  • Streaming support included via generate_stream().
  • No cloud. No API keys. Pure local inference.
"""

import json
import time
from typing import Any, Generator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaConnectionError(Exception):
    """Raised when the Ollama server cannot be reached."""


class OllamaModelError(Exception):
    """Raised when the requested model is not available."""


class OllamaTimeoutError(Exception):
    """Raised when an Ollama request exceeds the configured timeout."""


class OllamaResponseError(Exception):
    """Raised when Ollama returns an unexpected response."""


class AIService:
    """
    Primary service for all AI inference tasks in RAVAND OS.

    Responsibilities:
      - Maintain a persistent HTTP session with the Ollama server.
      - Route chat and generation requests to the correct endpoint.
      - Handle transient network failures with exponential back-off retry.
      - Extract token usage and timing metadata.
      - Provide a health check that confirms model availability.
      - Expose a streaming generator for real-time token delivery.

    Future extension points:
      - Vision: add image bytes to the messages payload.
      - Embeddings: call /api/embeddings for semantic search.
      - Multi-agent: call with different model names per agent role.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._session = self._build_http_session()
        logger.info(
            "AIService initialised | host=%s | model=%s",
            self._settings.OLLAMA_HOST,
            self._settings.OLLAMA_MODEL,
        )

    # ── HTTP Session ───────────────────────────────────────────────────────────

    def _build_http_session(self) -> requests.Session:
        """
        Build a requests.Session with connection-level retry logic.
        Retries are applied to connection errors and 5xx responses.
        Note: Ollama /api/generate uses POST and is NOT idempotent,
        so we retry only on connection-level failures, not on POST bodies.
        """
        session = requests.Session()
        retry_strategy = Retry(
        total=self._settings.OLLAMA_MAX_RETRIES,
        backoff_factor=self._settings.OLLAMA_RETRY_DELAY,
        status_forcelist=[502, 503, 504],
        allowed_methods={"GET", "POST"},
        raise_on_status=False,
)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    # ── Internal Request Helpers ───────────────────────────────────────────────

    def _post_with_retry(
        self,
        url: str,
        payload: dict[str, Any],
        stream: bool = False,
    ) -> requests.Response:
        """
        POST to an Ollama endpoint with manual retry logic.
        Retries on connection errors and timeouts.
        Raises OllamaConnectionError or OllamaTimeoutError on exhaustion.
        """
        last_error: Exception | None = None

        for attempt in range(1, self._settings.OLLAMA_MAX_RETRIES + 1):
            try:
                response = self._session.post(
                    url,
                    json=payload,
                    timeout=self._settings.OLLAMA_TIMEOUT,
                    stream=stream,
                )
                if response.status_code == 404:
                    raise OllamaModelError(
                        f"Model not found. Verify '{payload.get('model')}' is pulled in Ollama."
                    )
                response.raise_for_status()
                return response

            except requests.exceptions.Timeout as exc:
                last_error = exc
                logger.warning(
                    "Ollama request timed out (attempt %d/%d) | url=%s",
                    attempt,
                    self._settings.OLLAMA_MAX_RETRIES,
                    url,
                )
            except requests.exceptions.ConnectionError as exc:
                last_error = exc
                logger.warning(
                    "Ollama connection error (attempt %d/%d) | url=%s | error=%s",
                    attempt,
                    self._settings.OLLAMA_MAX_RETRIES,
                    url,
                    exc,
                )
            except OllamaModelError:
                raise
            except requests.exceptions.HTTPError as exc:
                raise OllamaResponseError(f"Ollama returned HTTP error: {exc}") from exc

            if attempt < self._settings.OLLAMA_MAX_RETRIES:
                sleep_time = self._settings.OLLAMA_RETRY_DELAY * attempt
                logger.debug("Retrying in %.1fs…", sleep_time)
                time.sleep(sleep_time)

        if isinstance(last_error, requests.exceptions.Timeout):
            raise OllamaTimeoutError(
                f"Ollama did not respond within {self._settings.OLLAMA_TIMEOUT}s "
                f"after {self._settings.OLLAMA_MAX_RETRIES} attempts."
            ) from last_error

        raise OllamaConnectionError(
            f"Cannot reach Ollama at {self._settings.OLLAMA_HOST}. "
            "Ensure Ollama is running: ollama serve"
        ) from last_error

    # ── Public API ─────────────────────────────────────────────────────────────

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 256,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """
        Send a multi-turn conversation to Ollama /api/chat.

        Args:
            messages:      List of {"role": ..., "content": ...} dicts.
            model:         Ollama model name. Defaults to OLLAMA_MODEL in config.
            temperature:   Sampling temperature (0.0–2.0).
            max_tokens:    Maximum tokens to generate.
            system_prompt: Optional system-level instruction injected as
                           the first message with role='system'.

        Returns:
            dict with keys:
                content       – the assistant response text
                model         – model that ran the inference
                prompt_tokens
                completion_tokens
                total_tokens
                duration_ms   – wall-clock time in milliseconds
        """
        target_model = model or self._settings.OLLAMA_MODEL
        full_messages = []

        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})

        full_messages.extend(messages)

        payload: dict[str, Any] = {
            "model": target_model,
            "messages": full_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        logger.debug(
            "chat() → model=%s | messages=%d | temperature=%.2f",
            target_model,
            len(full_messages),
            temperature,
        )
        start = time.perf_counter()
        response = self._post_with_retry(self._settings.ollama_api_chat, payload)
        duration_ms = int((time.perf_counter() - start) * 1000)

        data = response.json()
        
        # ✅ FIX: Ollama /api/chat returns content in message.content
        # Fallback to /api/generate format (response key) if message.content is empty
        content = data.get("message", {}).get("content", "")
        if not content:
            content = data.get("response", "")
        
        usage = data.get("usage", {})

        # Ollama reports token counts in 'eval_count' and 'prompt_eval_count'
        prompt_tokens = data.get("prompt_eval_count", usage.get("prompt_tokens", 0))
        completion_tokens = data.get("eval_count", usage.get("completion_tokens", 0))

        logger.info(
            "chat() ← model=%s | tokens=%d+%d | duration=%dms",
            target_model,
            prompt_tokens,
            completion_tokens,
            duration_ms,
        )

        return {
            "content": content,
            "model": target_model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "duration_ms": duration_ms,
        }

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """
        Single-turn text generation via Ollama /api/generate.
        Suitable for one-shot tasks: code generation, summarisation, etc.

        Args:
            prompt:        The full prompt string.
            model:         Ollama model name override.
            temperature:   Sampling temperature.
            max_tokens:    Maximum tokens to generate.
            system_prompt: Optional system-level instruction.

        Returns:
            Same structure as chat() – content, model, token counts, duration_ms.
        """
        target_model = model or self._settings.OLLAMA_MODEL

        payload: dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        logger.debug("generate() → model=%s | prompt_len=%d", target_model, len(prompt))
        start = time.perf_counter()
        response = self._post_with_retry(self._settings.ollama_api_generate, payload)
        duration_ms = int((time.perf_counter() - start) * 1000)

        data = response.json()
        
        # ✅ /api/generate uses "response" key directly
        content = data.get("response", "")
        
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        logger.info(
            "generate() ← model=%s | tokens=%d+%d | duration=%dms",
            target_model,
            prompt_tokens,
            completion_tokens,
            duration_ms,
        )

        return {
            "content": content,
            "model": target_model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "duration_ms": duration_ms,
        }

    def generate_stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: str | None = None,
    ) -> Generator[str, None, None]:
        """
        Streaming token generator via Ollama /api/generate with stream=True.
        Yields each token as it is produced by the model.

        Usage:
            for token in ai_service.generate_stream("Explain Newton's laws"):
                print(token, end="", flush=True)
        """
        target_model = model or self._settings.OLLAMA_MODEL

        payload: dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        logger.debug("generate_stream() → model=%s", target_model)

        response = self._post_with_retry(
            self._settings.ollama_api_generate,
            payload,
            stream=True,
        )

        for raw_line in response.iter_lines():
            if not raw_line:
                continue
            try:
                chunk = json.loads(raw_line)
                token = chunk.get("response", "")
                if token:
                    yield token
                if chunk.get("done", False):
                    break
            except json.JSONDecodeError:
                logger.warning("Unparseable stream chunk: %r", raw_line)

    def health(self) -> dict[str, Any]:
        """
        Check whether the Ollama server is reachable and the configured
        model is available.

        Returns:
            dict:
                reachable       – bool
                version         – Ollama version string or None
                model_loaded    – bool
                available_models – list[str]
        """
        result: dict[str, Any] = {
            "reachable": False,
            "version": None,
            "model_loaded": False,
            "available_models": [],
        }

        try:
            version_resp = self._session.get(
                self._settings.ollama_api_health,
                timeout=5,
            )
            if version_resp.ok:
                result["reachable"] = True
                result["version"] = version_resp.json().get("version")

            tags_resp = self._session.get(
                self._settings.ollama_api_tags,
                timeout=5,
            )
            if tags_resp.ok:
                models_data = tags_resp.json().get("models", [])
                names = [m.get("name", "") for m in models_data]
                result["available_models"] = names
                result["model_loaded"] = any(
                    self._settings.OLLAMA_MODEL in name for name in names
                )

        except requests.exceptions.ConnectionError:
            logger.warning("Ollama health check: server unreachable at %s", self._settings.OLLAMA_HOST)
        except Exception as exc:
            logger.error("Ollama health check failed unexpectedly: %s", exc)

        return result


# ── Singleton Factory ──────────────────────────────────────────────────────────

_ai_service_instance: AIService | None = None


def get_ai_service() -> AIService:
    """
    FastAPI dependency / module-level accessor for the AIService singleton.
    Creates the instance on first call; returns the cached instance thereafter.
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance