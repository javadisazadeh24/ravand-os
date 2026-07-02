import { decomposeTask } from "./decomposer";
import { executePlan } from "./executor";
import { AgentPlan } from "./types";

/**
 * MAIN AGENT CORE
 * Converts input → plan → execution
 */
export async function runAgent(input: string): Promise<AgentPlan> {
  const plan = decomposeTask(input);

  const result = await executePlan(plan);

  return result;
}