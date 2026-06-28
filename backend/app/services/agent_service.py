"""
RAVAND OS – Agent Service
=========================
Multi-agent framework for RAVAND OS.

Architecture:
  Each Agent is a specialised wrapper around AIService with:
    - A curated system prompt defining its expertise and persona.
    - A tool registry (callable Python functions injected as context).
    - Memory access (via MemoryService).
    - Structured reasoning steps (think → act → respond).

Available Agents:
  - GeneralAgent         – General-purpose assistant
  - CodingAgent          – Software development and debugging
  - EngineeringAgent     – Mechanical / structural engineering
  - DesignAgent          – Industrial and product design
  - TaskAutomationAgent  – Task planning and workflow automation

Extension:
  Add a new agent by subclassing BaseAgent, defining its SYSTEM_PROMPT
  and overriding _build_tool_context() if it needs specialised tools.
  Register it in AgentRegistry.
"""

from __future__ import annotations

import textwrap
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.ai_service import AIService, get_ai_service
from app.services.memory_service import MemoryService, get_memory_service

logger = get_logger(__name__)
settings = get_settings()


# ── Tool definition ────────────────────────────────────────────────────────────

class Tool:
    """
    A callable capability that an agent can invoke.

    Tools are not auto-called by the AI; they are described in the system
    prompt and the AI returns structured text that the tool dispatcher
    can parse. This is a lightweight "function calling" pattern without
    requiring model-native tool support.
    """

    def __init__(
        self,
        name: str,
        description: str,
        fn: Callable[..., Any],
    ) -> None:
        self.name = name
        self.description = description
        self.fn = fn

    def run(self, **kwargs: Any) -> Any:
        """Execute the tool function with provided keyword arguments."""
        logger.debug("Tool invoked | name=%s | kwargs=%s", self.name, kwargs)
        return self.fn(**kwargs)

    def describe(self) -> str:
        """Return a natural-language description for system prompt injection."""
        return f"  • {self.name}: {self.description}"


# ── Base Agent ─────────────────────────────────────────────────────────────────

class BaseAgent(ABC):
    """
    Abstract base class for all RAVAND OS agents.

    Every concrete agent must define:
      AGENT_NAME   – unique identifier
      SYSTEM_PROMPT – the agent's identity and expertise definition

    Agents share a common execution pattern:
      run() → enriches context → calls AIService → returns structured result
    """

    AGENT_NAME: str = "base"
    SYSTEM_PROMPT: str = ""

    def __init__(
        self,
        ai_service: AIService | None = None,
        memory_service: MemoryService | None = None,
    ) -> None:
        self._ai = ai_service or get_ai_service()
        self._memory = memory_service or get_memory_service()
        self._tools: dict[str, Tool] = {}
        self._register_tools()
        logger.debug("Agent initialised | name=%s", self.AGENT_NAME)

    def register_tool(self, tool: Tool) -> None:
        """Register a tool into this agent's tool registry."""
        self._tools[tool.name] = tool

    @abstractmethod
    def _register_tools(self) -> None:
        """Override to register agent-specific tools via self.register_tool()."""

    def _build_tool_context(self) -> str:
        """Generate the tools section for the system prompt."""
        if not self._tools:
            return ""
        lines = ["Available tools (describe what you need in text; the system will invoke them):"]
        lines.extend(t.describe() for t in self._tools.values())
        return "\n".join(lines)

    def _build_full_system_prompt(
        self,
        extra_context: str | None = None,
        memory_context: str | None = None,
    ) -> str:
        """Compose the complete system prompt for this agent invocation."""
        parts = [self.SYSTEM_PROMPT.strip()]

        tool_ctx = self._build_tool_context()
        if tool_ctx:
            parts.append(tool_ctx)

        if memory_context:
            parts.append(memory_context)

        if extra_context:
            parts.append(f"Additional context provided:\n{extra_context}")

        parts.append(
            f"\nCurrent timestamp: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        )
        return "\n\n".join(parts)

    def run(
        self,
        message: str,
        session_id: str,
        db: Session,
        extra_context: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        """
        Execute the agent on a single user message.

        Args:
            message:       The user's input.
            session_id:    Active session ID for memory access.
            db:            SQLAlchemy session for long-term memory.
            extra_context: Optional runtime context string to inject.
            temperature:   Sampling temperature.
            max_tokens:    Token limit for the response.

        Returns:
            dict with keys:
                agent       – agent name
                content     – response text
                model       – Ollama model used
                duration_ms – wall-clock inference time
                session_id  – echoed back
        """
        # Retrieve long-term memory relevant to this message
        memory_context = self._memory.get_long_term_context_string(
            db=db,
            query=message,
            session_id=session_id,
            limit=4,
        )

        # Retrieve short-term conversation history
        history = self._memory.get_short_term_context(
            session_id=session_id,
            limit=20,
        )

        # Append current user message to history before sending
        history.append({"role": "user", "content": message})

        system_prompt = self._build_full_system_prompt(
            extra_context=extra_context,
            memory_context=memory_context or None,
        )

        logger.info(
            "Agent run | agent=%s | session=%s | message_len=%d",
            self.AGENT_NAME,
            session_id,
            len(message),
        )

        result = self._ai.chat(
            messages=history,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Update short-term memory
        self._memory.add_to_short_term(session_id, "user", message)
        self._memory.add_to_short_term(session_id, "assistant", result["content"])

        return {
            "agent": self.AGENT_NAME,
            "content": result["content"],
            "model": result["model"],
            "duration_ms": result.get("duration_ms", 0),
            "session_id": session_id,
            "prompt_tokens": result.get("prompt_tokens", 0),
            "completion_tokens": result.get("completion_tokens", 0),
        }


# ── Concrete Agents ────────────────────────────────────────────────────────────

class GeneralAgent(BaseAgent):
    """
    General-purpose conversational assistant for RAVAND OS.
    Handles everyday queries, explanations, and general knowledge.
    """

    AGENT_NAME = "general"
    SYSTEM_PROMPT = textwrap.dedent("""
        You are RAVAND OS General Assistant, an intelligent offline AI assistant
        developed for FabLab Ravand – a knowledge-based engineering and fabrication lab.

        Your capabilities:
        - Answer questions across science, engineering, business, and general knowledge.
        - Explain concepts clearly in the user's language (Persian or English).
        - Assist with planning, writing, research, and problem-solving.
        - You run entirely offline with no internet access.
        - Never mention OpenAI, ChatGPT, Google, or any cloud service.
        - Be concise, factual, and professional.
    """).strip()

    def _register_tools(self) -> None:
        self.register_tool(Tool(
            name="get_current_time",
            description="Return the current date and time.",
            fn=lambda: datetime.now(tz=timezone.utc).isoformat(),
        ))


class CodingAgent(BaseAgent):
    """
    Software development and debugging assistant.
    Specialises in Python, backend systems, APIs, and tooling.
    """

    AGENT_NAME = "coding"
    SYSTEM_PROMPT = textwrap.dedent("""
        You are RAVAND OS Coding Agent, an expert software engineer and architect.

        Specialisations:
        - Python 3.12+, FastAPI, SQLAlchemy, Pydantic v2
        - REST API design and implementation
        - Database schema design
        - Debugging and code review
        - Shell scripting and automation
        - Git workflows
        - Clean Architecture and SOLID principles

        Rules:
        - Always produce complete, runnable code. No pseudo-code. No TODOs.
        - Include type hints and docstrings.
        - Explain each code block after producing it.
        - Prefer standard library solutions when possible.
        - Warn about potential pitfalls and edge cases.
        - You are offline. Do not suggest cloud services or external APIs.
    """).strip()

    def _register_tools(self) -> None:
        pass  # Future: code execution sandbox, linter integration


class EngineeringAgent(BaseAgent):
    """
    Mechanical and structural engineering assistant.
    Supports FabLab Ravand's engineering operations.
    """

    AGENT_NAME = "engineering"
    SYSTEM_PROMPT = textwrap.dedent("""
        You are RAVAND OS Engineering Agent, a senior mechanical and structural engineer.

        Domain expertise:
        - Mechanical design and analysis
        - Material selection (metals, polymers, composites)
        - Stress, strain, and fatigue analysis fundamentals
        - CNC machining – toolpaths, feeds, speeds, tolerances
        - 3D printing – FDM, SLA, material properties, design for additive manufacturing
        - Reverse engineering workflows
        - GD&T (Geometric Dimensioning and Tolerancing)
        - Prototype and mould design
        - Engineering standards and calculations

        Rules:
        - Provide precise technical answers with relevant formulas when applicable.
        - Always include units for all quantities.
        - If uncertain, state so explicitly and suggest verification steps.
        - Prefer practical, implementable recommendations.
        - Respond in the user's language (Persian or English).
    """).strip()

    def _register_tools(self) -> None:
        self.register_tool(Tool(
            name="unit_convert",
            description=(
                "Convert between engineering units. "
                "Provide: value, from_unit, to_unit."
            ),
            fn=self._unit_convert,
        ))

    @staticmethod
    def _unit_convert(value: float, from_unit: str, to_unit: str) -> str:
        """
        Simple unit conversion for common engineering quantities.
        Extend with a proper unit library (e.g., pint) for production use.
        """
        conversions: dict[tuple[str, str], float] = {
            ("mm", "inch"): 0.0393701,
            ("inch", "mm"): 25.4,
            ("kg", "lb"): 2.20462,
            ("lb", "kg"): 0.453592,
            ("mpa", "psi"): 145.038,
            ("psi", "mpa"): 0.00689476,
            ("m", "ft"): 3.28084,
            ("ft", "m"): 0.3048,
        }
        key = (from_unit.lower(), to_unit.lower())
        factor = conversions.get(key)
        if factor is None:
            return f"Conversion from {from_unit} to {to_unit} not available."
        result = value * factor
        return f"{value} {from_unit} = {result:.6g} {to_unit}"


class DesignAgent(BaseAgent):
    """
    Industrial and product design assistant.
    Supports conceptual design, ergonomics, and manufacturing considerations.
    """

    AGENT_NAME = "design"
    SYSTEM_PROMPT = textwrap.dedent("""
        You are RAVAND OS Design Agent, a senior industrial designer and product engineer.

        Domain expertise:
        - Industrial design principles and methodology
        - Human factors and ergonomics
        - Design for manufacturing (DFM) and assembly (DFA)
        - Material aesthetics and surface finishing
        - Conceptual sketching and ideation (text-based guidance)
        - Rapid prototyping strategies
        - Packaging and form factor design
        - Design communication and specification writing
        - Colour theory and visual design fundamentals
        - Design standards (ISO, DIN) and intellectual property considerations

        Working context:
        - FabLab Ravand has: Creality Ender 3 V3 Plus (FDM), Tekno CNC machine
        - Consider available fabrication capabilities when advising
        - Always balance aesthetics with manufacturability

        Rules:
        - Ask clarifying questions if requirements are ambiguous.
        - Describe design concepts in structured, visualisable language.
        - Provide material and process recommendations with justification.
        - Respond in the user's language (Persian or English).
    """).strip()

    def _register_tools(self) -> None:
        pass  # Future: image generation via local diffusion model


class TaskAutomationAgent(BaseAgent):
    """
    Task planning and workflow automation agent.
    Breaks complex goals into structured, executable steps.
    """

    AGENT_NAME = "task_automation"
    SYSTEM_PROMPT = textwrap.dedent("""
        You are RAVAND OS Task Automation Agent, an expert project manager and
        workflow designer.

        Capabilities:
        - Decompose complex goals into ordered, actionable tasks
        - Create structured project plans with dependencies
        - Identify risks and blockers
        - Suggest automation opportunities
        - Write shell scripts and Python automation for local workflows
        - Design checklists and standard operating procedures
        - Estimate time and resource requirements

        Output format preferences:
        - Use numbered steps for sequences
        - Use checklists for parallel tasks
        - Include time estimates where relevant
        - Flag blockers and prerequisites clearly
        - Offer a brief summary before detailed steps

        Rules:
        - You are offline. All automation must run locally on Windows.
        - Prefer Python for scripting. Batch scripts as fallback.
        - Validate that each step is achievable before including it.
    """).strip()

    def _register_tools(self) -> None:
        self.register_tool(Tool(
            name="create_task_outline",
            description="Structure a goal into a task breakdown with phases and steps.",
            fn=lambda goal: f"Task outline for: {goal}\n[Generated by TaskAutomationAgent]",
        ))


# ── Agent Registry ─────────────────────────────────────────────────────────────

class AgentRegistry:
    """
    Central registry of all available RAVAND OS agents.

    Usage:
        registry = AgentRegistry()
        agent = registry.get("coding")
        result = agent.run(message="Write a quicksort", session_id=..., db=...)
    """

    def __init__(
        self,
        ai_service: AIService | None = None,
        memory_service: MemoryService | None = None,
    ) -> None:
        _ai = ai_service or get_ai_service()
        _mem = memory_service or get_memory_service()

        self._agents: dict[str, BaseAgent] = {
            agent.AGENT_NAME: agent
            for agent in [
                GeneralAgent(_ai, _mem),
                CodingAgent(_ai, _mem),
                EngineeringAgent(_ai, _mem),
                DesignAgent(_ai, _mem),
                TaskAutomationAgent(_ai, _mem),
            ]
        }
        logger.info(
            "AgentRegistry initialised | agents=%s",
            list(self._agents.keys()),
        )

    def get(self, agent_name: str) -> BaseAgent:
        """
        Return the agent for the given name.
        Raises KeyError if the agent does not exist.
        """
        if agent_name not in self._agents:
            raise KeyError(
                f"Agent '{agent_name}' not found. "
                f"Available agents: {self.list_agents()}"
            )
        return self._agents[agent_name]

    def list_agents(self) -> list[str]:
        """Return a sorted list of all registered agent names."""
        return sorted(self._agents.keys())

    def list_agent_info(self) -> list[dict[str, str]]:
        """Return name + class description for all registered agents."""
        return [
            {
                "name": name,
                "class": type(agent).__name__,
                "description": (type(agent).__doc__ or "").strip().split("\n")[0],
            }
            for name, agent in self._agents.items()
        ]


# ── Agent Service ──────────────────────────────────────────────────────────────

class AgentService:
    """
    Application-layer service for agent orchestration.
    Wraps AgentRegistry with logging and structured error handling.
    """

    def __init__(
        self,
        ai_service: AIService | None = None,
        memory_service: MemoryService | None = None,
    ) -> None:
        self._registry = AgentRegistry(
            ai_service=ai_service,
            memory_service=memory_service,
        )
        logger.info("AgentService ready.")

    def run_agent(
        self,
        agent_name: str,
        message: str,
        session_id: str,
        db: Session,
        extra_context: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        """
        Execute the named agent on the given message.

        Args:
            agent_name:    Name of the agent to invoke.
            message:       User's input message.
            session_id:    Active session ID.
            db:            SQLAlchemy session for memory.
            extra_context: Optional context string.
            temperature:   Sampling temperature.
            max_tokens:    Response token limit.

        Returns:
            Structured result dict from the agent's run() method.

        Raises:
            KeyError if agent_name is not registered.
        """
        agent = self._registry.get(agent_name)
        return agent.run(
            message=message,
            session_id=session_id,
            db=db,
            extra_context=extra_context,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def list_agents(self) -> list[dict[str, str]]:
        """Return info about all available agents."""
        return self._registry.list_agent_info()


# ── Singleton ──────────────────────────────────────────────────────────────────

_agent_service_instance: AgentService | None = None


def get_agent_service() -> AgentService:
    """FastAPI dependency for the AgentService singleton."""
    global _agent_service_instance
    if _agent_service_instance is None:
        _agent_service_instance = AgentService()
    return _agent_service_instance
