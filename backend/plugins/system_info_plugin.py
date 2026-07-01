"""
RAVAND OS – Example Plugin: System Info
========================================
This file serves as a reference implementation for plugin developers.

Place plugin files in the /backend/plugins/ directory.
The PluginLoader will auto-discover and load them at startup.

Copy and rename this file to build your own plugin.
"""

import platform
import time
from typing import Any

from app.services.plugin_service import BasePlugin, EventBus


class Plugin(BasePlugin):
    """
    System Info Plugin for RAVAND OS.
    Provides local machine information as a tool for agents.
    Subscribes to chat events and logs them for diagnostics.
    """

    NAME = "system_info"
    VERSION = "1.0.0"
    DESCRIPTION = "Exposes local system information to RAVAND OS agents."

    def on_load(self) -> None:
        """Subscribe to events and initialise the plugin."""
        self.event_bus.subscribe("chat.message_received", self._on_chat_message)
        self.event_bus.subscribe("plugin.loaded", self._on_plugin_loaded)
        self._message_count = 0
        self._start_time = time.time()
        print(f"[{self.NAME}] Plugin loaded successfully.")

    def on_unload(self) -> None:
        """Clean up event subscriptions."""
        self.event_bus.unsubscribe("chat.message_received", self._on_chat_message)
        self.event_bus.unsubscribe("plugin.loaded", self._on_plugin_loaded)
        print(f"[{self.NAME}] Plugin unloaded. Processed {self._message_count} messages.")

    def register_tools(self, agent_registry: Any) -> None:
        """
        Inject the get_system_info tool into the GeneralAgent.
        This demonstrates how plugins extend agents without modifying core code.
        """
        from app.services.plugin_service import Tool

        tool = Tool(
            name="get_system_info",
            description="Return local machine OS, CPU, and memory information.",
            fn=self._get_system_info,
        )
        try:
            general_agent = agent_registry.get("general")
            general_agent.register_tool(tool)
            print(f"[{self.NAME}] Tool 'get_system_info' registered with GeneralAgent.")
        except KeyError:
            print(f"[{self.NAME}] GeneralAgent not found – tool registration skipped.")

    def health_check(self) -> dict[str, Any]:
        """Return plugin health and runtime statistics."""
        base = super().health_check()
        base["messages_processed"] = self._message_count
        base["uptime_seconds"] = round(time.time() - self._start_time, 1)
        return base

    # ── Event Handlers ─────────────────────────────────────────────────────────

    def _on_chat_message(self, payload: dict[str, Any]) -> None:
        """Count incoming chat messages for diagnostics."""
        self._message_count += 1

    def _on_plugin_loaded(self, payload: dict[str, Any]) -> None:
        """Log when another plugin is loaded."""
        if payload.get("name") != self.NAME:
            print(f"[{self.NAME}] Another plugin loaded: {payload.get('name')}")

    # ── Tool Implementation ────────────────────────────────────────────────────

    @staticmethod
    def _get_system_info() -> dict[str, str]:
        """Return key local system properties."""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
        }
