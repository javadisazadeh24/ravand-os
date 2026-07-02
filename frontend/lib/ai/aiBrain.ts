import { parseCommand } from "../commandEngine";
import { runPlugins } from "./plugins";
import { useMemoryStore } from "@/store/useMemoryStore";

/**
 * RAVAND OS — AI Brain Core (v1.5)
 * Offline-first + Memory-aware + Plugin-driven
 */

export type AIIntent =
  | "navigation"
  | "action"
  | "query"
  | "plugin"
  | "unknown";

export type AIDecision = {
  intent: AIIntent;
  confidence: number;

  target?: string;
  response?: string;

  meta?: {
    source: "plugin" | "rules" | "memory" | "fallback";
    rawInput: string;
  };
};

/**
 * MEMORY LOGGER
 */
function saveMemory(
  content: string,
  type: "command" | "navigation" | "note"
) {
  const memoryStore = useMemoryStore.getState();

  memoryStore.addMemory({
    id: crypto.randomUUID(),
    content,
    type,
    timestamp: Date.now(),
  });
}

/**
 * MEMORY CONTEXT BUILDER
 */
function getMemoryContext(limit = 5) {
  const memoryStore = useMemoryStore.getState();

  return memoryStore.memories
    .slice(0, limit)
    .map((m) => `[${m.type}] ${m.content}`)
    .join(" | ");
}

/**
 * MAIN AI BRAIN
 */
export function aiBrain(input: string): AIDecision {
  const normalized = input.trim().toLowerCase();

  const memoryContext = getMemoryContext();

  /**
   * 1. PLUGIN LAYER (highest priority)
   */
  const pluginResult = runPlugins(normalized);

  if (pluginResult) {
    saveMemory(input, "note");

    return {
      intent: "plugin",
      confidence: 0.98,
      response: pluginResult,
      meta: {
        source: "plugin",
        rawInput: input,
      },
    };
  }

  /**
   * 2. COMMAND PARSER LAYER
   */
  const command = parseCommand(normalized);

  // NAVIGATION
  if (command.type === "navigation" && command.target) {
    saveMemory(input, "navigation");

    return {
      intent: "navigation",
      confidence: 0.95,
      target: command.target,
      meta: {
        source: "rules",
        rawInput: input,
      },
    };
  }

  // ACTION
  if (command.type === "action") {
    saveMemory(input, "command");

    return {
      intent: "action",
      confidence: 0.9,
      response: command.message || "Action executed in OS layer.",
      meta: {
        source: "rules",
        rawInput: input,
      },
    };
  }

  /**
   * 3. QUERY DETECTION (light NLP rules)
   */
  const isQuestion =
    normalized.includes("?") ||
    normalized.startsWith("what") ||
    normalized.startsWith("how") ||
    normalized.startsWith("why") ||
    normalized.startsWith("when") ||
    normalized.startsWith("who");

  if (isQuestion) {
    saveMemory(input, "note");

    return {
      intent: "query",
      confidence: 0.65,
      response:
        "Query detected. No external model is active yet. OS memory + plugins available.",
      meta: {
        source: "rules",
        rawInput: input,
      },
    };
  }

  /**
   * 4. KEYWORD NAVIGATION DETECTION
   */
  if (normalized.includes("open") || normalized.includes("go to")) {
    const target = normalized
      .replace("open", "")
      .replace("go to", "")
      .trim();

    saveMemory(input, "navigation");

    return {
      intent: "navigation",
      confidence: 0.6,
      target: `/${target}`,
      meta: {
        source: "rules",
        rawInput: input,
      },
    };
  }

  /**
   * 5. MEMORY-AWARE FALLBACK
   */
  saveMemory(input, "note");

  return {
    intent: "unknown",
    confidence: 0.35,
    response: memoryContext
      ? `Command not recognized.\n\nRecent context:\n${memoryContext}`
      : "Command not recognized by AI Brain.",
    meta: {
      source: "memory",
      rawInput: input,
    },
  };
}