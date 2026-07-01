"""
RAVAND OS – Plugin System
=========================
Provides a lightweight plugin architecture for extending RAVAND OS
without modifying core code.

Plugin contract:
  A plugin is a Python module (.py file) placed in the plugins/ directory.
  It must expose a class named Plugin that inherits from BasePlugin.

  Minimum required implementation:
    class Plugin(BasePlugin):
        NAME        = "my_plugin"
        VERSION     = "1.0.0"
        DESCRIPTION = "What this plugin does."

        def on_load(self) -> None:
            # initialisation logic

        def on_unload(self) -> None:
            # cleanup logic

Event system:
  Plugins communicate with the core and each other via the EventBus.
  Any component can emit an event; any plugin can subscribe to events.

  Example:
      bus = get_event_bus()
      bus.subscribe("chat.message_received", my_handler)
      bus.emit("chat.message_received", {"session_id": ..., "content": ...})

Tool injection:
  Plugins may register tools into the AgentService's tool registries
  via plugin.register_tools(agent_registry).
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Event Bus ─────────────────────────────────────────────────────────────────

EventHandler = Callable[[dict[str, Any]], None]


class EventBus:
    """
    Lightweight synchronous event bus for inter-plugin and plugin-core
    communication.

    Events are identified by string names using dot notation:
      'chat.message_received'
      'memory.stored'
      'task.completed'
      'plugin.loaded'

    Subscriptions are stored in memory and reset on restart.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event: str, handler: EventHandler) -> None:
        """
        Register a handler to be called when `event` is emitted.

        Args:
            event:   Event name string.
            handler: Callable that accepts a dict payload.
        """
        self._subscribers[event].append(handler)
        logger.debug("EventBus: subscribed | event=%s | handler=%s", event, handler.__qualname__)

    def unsubscribe(self, event: str, handler: EventHandler) -> None:
        """Remove a specific handler from an event's subscriber list."""
        handlers = self._subscribers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event: str, payload: dict[str, Any] | None = None) -> int:
        """
        Emit an event to all registered subscribers.

        Args:
            event:   Event name.
            payload: Optional data dict passed to each handler.

        Returns:
            Number of handlers invoked.
        """
        handlers = self._subscribers.get(event, [])
        payload = payload or {}
        invoked = 0
        for handler in handlers:
            try:
                handler(payload)
                invoked += 1
            except Exception as exc:
                logger.error(
                    "EventBus: handler error | event=%s | handler=%s | error=%s",
                    event,
                    handler.__qualname__,
                    exc,
                )
        logger.debug("EventBus: emitted | event=%s | handlers=%d", event, invoked)
        return invoked

    def list_events(self) -> list[str]:
        """Return a sorted list of all event names with subscribers."""
        return sorted(self._subscribers.keys())


# ── Base Plugin ────────────────────────────────────────────────────────────────

class BasePlugin(ABC):
    """
    Abstract base class for all RAVAND OS plugins.

    Every plugin must define:
        NAME        – unique snake_case identifier
        VERSION     – semantic version string
        DESCRIPTION – one-line description

    And implement:
        on_load()   – called when the plugin is loaded
        on_unload() – called when the plugin is removed or system shuts down
    """

    NAME: str = "unnamed_plugin"
    VERSION: str = "0.0.1"
    DESCRIPTION: str = ""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self._loaded_at: float | None = None

    @abstractmethod
    def on_load(self) -> None:
        """Initialise the plugin. Subscribe to events here."""

    @abstractmethod
    def on_unload(self) -> None:
        """Clean up resources and unsubscribe from events."""

    def register_tools(self, agent_registry: Any) -> None:
        """
        Optional: inject tools into agents from this plugin.
        Override in subclass to add tools to specific agents.
        """

    def health_check(self) -> dict[str, Any]:
        """
        Return plugin health status.
        Override for custom health logic.
        """
        return {
            "name": self.NAME,
            "version": self.VERSION,
            "loaded": self._loaded_at is not None,
            "loaded_at": self._loaded_at,
        }

    def __repr__(self) -> str:
        return f"<Plugin name={self.NAME!r} version={self.VERSION!r}>"


# ── Plugin Registry ───────────────────────────────────────────────────────────

class PluginRegistry:
    """
    Tracks all loaded plugin instances.
    Provides lookup by name and iteration.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> None:
        if plugin.NAME in self._plugins:
            raise ValueError(f"Plugin '{plugin.NAME}' is already registered.")
        self._plugins[plugin.NAME] = plugin
        logger.info("Plugin registered | name=%s | version=%s", plugin.NAME, plugin.VERSION)

    def unregister(self, name: str) -> bool:
        if name not in self._plugins:
            return False
        del self._plugins[name]
        logger.info("Plugin unregistered | name=%s", name)
        return True

    def get(self, name: str) -> BasePlugin | None:
        return self._plugins.get(name)

    def all(self) -> list[BasePlugin]:
        return list(self._plugins.values())

    def names(self) -> list[str]:
        return sorted(self._plugins.keys())


# ── Plugin Loader ─────────────────────────────────────────────────────────────

class PluginLoader:
    """
    Discovers and loads plugin modules from a directory.

    Loading process:
      1. Scan the plugins_dir for *.py files.
      2. Import each as a module.
      3. Find the class named 'Plugin' that subclasses BasePlugin.
      4. Instantiate and call on_load().
      5. Register in PluginRegistry.

    Error isolation:
      A broken plugin is skipped and logged; it does not crash the system.
    """

    def __init__(
        self,
        plugins_dir: Path,
        event_bus: EventBus,
        registry: PluginRegistry,
    ) -> None:
        self._plugins_dir = plugins_dir
        self._event_bus = event_bus
        self._registry = registry

    def discover_and_load(self) -> list[str]:
        """
        Scan plugins_dir and load all valid plugin files.

        Returns:
            List of successfully loaded plugin names.
        """
        if not self._plugins_dir.exists():
            logger.warning(
                "Plugins directory does not exist | path=%s",
                self._plugins_dir,
            )
            self._plugins_dir.mkdir(parents=True, exist_ok=True)
            return []

        loaded: list[str] = []
        for plugin_file in sorted(self._plugins_dir.glob("*.py")):
            if plugin_file.stem.startswith("_"):
                continue  # skip __init__.py and private files
            name = self._load_file(plugin_file)
            if name:
                loaded.append(name)

        logger.info(
            "Plugin discovery complete | loaded=%d | dir=%s",
            len(loaded),
            self._plugins_dir,
        )
        return loaded

    def _load_file(self, path: Path) -> str | None:
        """
        Load a single plugin file. Returns the plugin NAME on success, None on failure.
        Errors are caught and logged without propagating.
        """
        module_name = f"ravand_plugin_{path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                logger.warning("Cannot build module spec | path=%s", path)
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)  # type: ignore[union-attr]

            # Find the Plugin class in the module
            plugin_class = getattr(module, "Plugin", None)
            if plugin_class is None:
                logger.warning("No 'Plugin' class found | file=%s", path.name)
                return None

            if not (inspect.isclass(plugin_class) and issubclass(plugin_class, BasePlugin)):
                logger.warning(
                    "'Plugin' class does not inherit BasePlugin | file=%s", path.name
                )
                return None

            instance: BasePlugin = plugin_class(event_bus=self._event_bus)
            instance._loaded_at = time.time()
            instance.on_load()
            self._registry.register(instance)

            self._event_bus.emit(
                "plugin.loaded",
                {"name": instance.NAME, "version": instance.VERSION},
            )
            logger.info("Plugin loaded | name=%s | file=%s", instance.NAME, path.name)
            return instance.NAME

        except Exception as exc:
            logger.error(
                "Failed to load plugin | file=%s | error=%s",
                path.name,
                exc,
                exc_info=True,
            )
            return None

    def unload(self, name: str) -> bool:
        """
        Call on_unload() on a plugin and remove it from the registry.

        Returns True if found and unloaded, False if not found.
        """
        plugin = self._registry.get(name)
        if not plugin:
            return False
        try:
            plugin.on_unload()
        except Exception as exc:
            logger.error("Plugin on_unload() error | name=%s | %s", name, exc)

        self._registry.unregister(name)
        self._event_bus.emit("plugin.unloaded", {"name": name})
        return True


# ── Plugin Service (application layer) ────────────────────────────────────────

class PluginService:
    """
    Application-layer facade for the plugin system.
    Owns the EventBus, PluginRegistry, and PluginLoader.
    Used as a FastAPI dependency and during startup.
    """

    def __init__(self, plugins_dir: Path | str | None = None) -> None:
        self.event_bus = EventBus()
        self.registry = PluginRegistry()
        _dir = Path(plugins_dir) if plugins_dir else Path("plugins")
        self.loader = PluginLoader(
            plugins_dir=_dir,
            event_bus=self.event_bus,
            registry=self.registry,
        )
        logger.info("PluginService initialised | plugins_dir=%s", _dir)

    def startup(self) -> list[str]:
        """
        Called at application startup. Discovers and loads all plugins.
        Returns list of loaded plugin names.
        """
        return self.loader.discover_and_load()

    def shutdown(self) -> None:
        """Unload all plugins gracefully during application shutdown."""
        for name in list(self.registry.names()):
            self.loader.unload(name)
        logger.info("All plugins unloaded.")

    def emit(self, event: str, payload: dict[str, Any] | None = None) -> int:
        """Emit an event on the shared EventBus."""
        return self.event_bus.emit(event, payload)

    def list_plugins(self) -> list[dict[str, Any]]:
        """Return summary info for all loaded plugins."""
        return [p.health_check() for p in self.registry.all()]

    def get_plugin(self, name: str) -> BasePlugin | None:
        """Return a plugin by name, or None."""
        return self.registry.get(name)


# ── Singleton ──────────────────────────────────────────────────────────────────

_plugin_service_instance: PluginService | None = None


def get_plugin_service() -> PluginService:
    """FastAPI dependency for the PluginService singleton."""
    global _plugin_service_instance
    if _plugin_service_instance is None:
        _plugin_service_instance = PluginService()
    return _plugin_service_instance
