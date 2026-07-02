import { AgentPlan, type AgentStep } from "./types";

/**
 * Simple rule-based task decomposition engine
 */
export function decomposeTask(input: string): AgentPlan {
  const normalized = input.toLowerCase();

  const steps: AgentStep[] = [];

  // NAVIGATION TASK
  if (normalized.includes("open") || normalized.includes("go to")) {
    steps.push({
      id: crypto.randomUUID(),
      action: "navigate",
      target: "/target",
      status: "pending",
    });
  }

  // DATA TASK
  if (normalized.includes("show") || normalized.includes("list")) {
    steps.push({
      id: crypto.randomUUID(),
      action: "fetch_data",
      status: "pending",
    });
  }

  // DEFAULT TASK
  if (steps.length === 0) {
    steps.push({
      id: crypto.randomUUID(),
      action: "interpret",
      status: "pending",
    });
  }

  return {
    id: crypto.randomUUID(),
    originalInput: input,
    steps,
    status: "created",
  };
}
