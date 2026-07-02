import { parseCommand } from "../commandEngine";
import { runPlugins } from "./plugins";
import { useMemoryStore } from "@/store/useMemoryStore";
import { runAgent } from "../agent/agent";

/**
 * 🧠 RAVAND OS — AI Brain v2 (FINAL)
 * - Plugin layer
 * - Command system
 * - Memory awareness
 * - Agent execution
 * - Structured OS output
 */

export type AIIntent =
  | "navigation"
  | "action"
  | "query"
  | "plugin"
  | "agent"
  | "unknown";

export type AIDecision = {
  intent: AIIntent;
  confidence: number;

  response?: string;
  target?: string;

  meta?: {
    source: "plugin" | "rules" | "memory" | "agent" | "fallback";
    rawInput: string;
  };
};

/* -----------------------------
   MEMORY SYSTEM
------------------------------ */

function saveMemory(
  content: string,
  type: "command" | "navigation" | "note"
) {
  const store = useMemoryStore.getState();

  store.addMemory({
    id: crypto.randomUUID(),
    content,
    type,
    timestamp: Date.now(),
  });
}

function getMemoryContext(limit = 5) {
  const store = useMemoryStore.getState();

  return store.memories
    .slice(0, limit)
    .map((m) => `[${m.type}] ${m.content}`)
    .join(" | ");
}

/* -----------------------------
   MAIN AI BRAIN
------------------------------ */

export async function aiBrain(input: string): Promise<AIDecision> {
  const normalized = input.trim().toLowerCase();
  const memoryContext = getMemoryContext();

  /* -------------------------
     1. PLUGIN LAYER (HIGHEST PRIORITY)
  -------------------------- */

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

  /* -------------------------
     2. COMMAND PARSER
  -------------------------- */

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
      response:
        command.message || "Action executed in OS layer.",
      meta: {
        source: "rules",
        rawInput: input,
      },
    };
  }

  /* -------------------------
     3. AGENT MODE (AUTONOMOUS EXECUTION)
  -------------------------- */

  if (
    normalized.includes("agent") ||
    normalized.includes("auto") ||
    normalized.includes("run task") ||
    normalized.includes("execute plan")
  ) {
    saveMemory(input, "command");

    const result = await runAgent(input);

    return {
      intent: "agent",
      confidence: 0.99,
      response: JSON.stringify(result, null, 2),
      meta: {
        source: "agent",
        rawInput: input,
      },
    };
  }

  /* -------------------------
     4. QUESTION DETECTION
  -------------------------- */

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
      confidence: 0.7,
      response:
        "Query detected. AI Brain is running in rules + memory + plugin mode (no LLM yet).",
      meta: {
        source: "rules",
        rawInput: input,
      },
    };
  }

  /* -------------------------
     5. SIMPLE NAVIGATION KEYWORDS
  -------------------------- */

  if (
    normalized.includes("open") ||
    normalized.includes("go to")
  ) {
    const target = normalized
      .replace("open", "")
      .replace("go to", "")
      .trim();

    saveMemory(input, "navigation");

    return {
      intent: "navigation",
      confidence: 0.65,
      target: `/${target}`,
      meta: {
        source: "rules",
        rawInput: input,
      },
    };
  }

  /* -------------------------
     6. FALLBACK (MEMORY-AWARE)
  -------------------------- */

  saveMemory(input, "note");

  return {
    intent: "unknown",
    confidence: 0.4,
    response: memoryContext
      ? `Command not recognized.\n\nMemory context:\n${memoryContext}`
      : "Command not recognized by AI Brain.",
    meta: {
      source: "memory",
      rawInput: input,
    },
  };
}