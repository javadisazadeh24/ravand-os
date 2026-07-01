"""
RAVAND OS – Knowledge Service
Manages the system prompt / knowledge base injected into every AI conversation.

Design intent:
  This service acts as the "long-term memory" layer between raw user messages
  and the AI engine. Currently it returns static company knowledge.
  Future versions will pull from a vector store or SQLite knowledge base for
  dynamic retrieval-augmented generation (RAG).

Extension points (documented for future developers):
  - add_document()     → chunk + embed → store in vector DB
  - search_knowledge() → semantic search → top-k chunks
  - The returned system prompt will automatically include retrieved chunks.
"""

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Default system prompt template ────────────────────────────────────────────
_SYSTEM_PROMPT_TEMPLATE = """
You are RAVAND OS, an intelligent offline AI assistant developed for {company_name}.

About {company_name}:
{company_name} is a knowledge-based engineering company ({tagline}).
Location: {location}
Core services:
{services_list}

Your role:
- Answer questions professionally and accurately.
- Assist with engineering, design, fabrication, and business tasks.
- You run entirely offline. You have no internet access.
- Never mention ChatGPT, OpenAI, Google, or cloud AI services.
- Respond in the same language the user writes in (Persian or English).
- Be concise, structured, and technically accurate.
- When asked about the company, use only the information provided above.
""".strip()


class KnowledgeService:
    """
    Provides context-enriched system prompts for the AI engine.

    Currently implements static company knowledge injection.
    Designed to evolve into a full RAG pipeline without API changes.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._base_system_prompt = self._build_base_system_prompt()
        logger.debug(
            "KnowledgeService initialised | company=%s",
            self._settings.COMPANY_NAME,
        )

    def _build_base_system_prompt(self) -> str:
        """Build the static system prompt from company configuration."""
        services_lines = "\n".join(
            f"  • {svc}" for svc in self._settings.COMPANY_SERVICES
        )
        return _SYSTEM_PROMPT_TEMPLATE.format(
            company_name=self._settings.COMPANY_NAME,
            tagline=self._settings.COMPANY_TAGLINE,
            location=self._settings.COMPANY_LOCATION,
            services_list=services_lines,
        )

    def get_system_prompt(self, user_context: str | None = None) -> str:
        """
        Return the full system prompt to inject into an AI conversation.

        Args:
            user_context: Optional additional context string appended to
                          the base prompt (e.g., from a retrieved knowledge chunk).

        Returns:
            Complete system prompt string.
        """
        if user_context:
            return f"{self._base_system_prompt}\n\nAdditional context:\n{user_context}"
        return self._base_system_prompt

    def get_company_context(self) -> dict:
        """
        Return structured company information for API responses.
        Used by the /company endpoint.
        """
        return {
            "name": self._settings.COMPANY_NAME,
            "tagline": self._settings.COMPANY_TAGLINE,
            "location": self._settings.COMPANY_LOCATION,
            "services": self._settings.COMPANY_SERVICES,
        }

    # ── Future RAG hooks ───────────────────────────────────────────────────────

    def add_document(self, title: str, content: str, source: str = "manual") -> None:
        """
        [FUTURE] Chunk, embed, and store a document in the knowledge base.
        Currently a no-op stub ready for implementation.
        """
        logger.info(
            "add_document() called | title=%r | source=%r (RAG not yet implemented)",
            title,
            source,
        )

    def search_knowledge(self, query: str, top_k: int = 3) -> list[str]:
        """
        [FUTURE] Semantic search over the knowledge base.
        Returns relevant text chunks for RAG injection.
        Currently returns an empty list.
        """
        logger.debug("search_knowledge() | query=%r | top_k=%d (stub)", query, top_k)
        return []


# ── Singleton ──────────────────────────────────────────────────────────────────

_knowledge_service_instance: KnowledgeService | None = None


def get_knowledge_service() -> KnowledgeService:
    """FastAPI dependency for the KnowledgeService singleton."""
    global _knowledge_service_instance
    if _knowledge_service_instance is None:
        _knowledge_service_instance = KnowledgeService()
    return _knowledge_service_instance
