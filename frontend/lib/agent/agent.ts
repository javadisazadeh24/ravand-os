import { createPlan } from "./planner";
import { runTool } from "../tools/toolRouter";
import { eventBus } from "../core/eventBus";

type AgentExecutionResult = {
  step: string;
  result?: unknown;
  error?: string;
};

/**
 * 🧠 RAVAND OS — Event-driven Agent Executor
 */

export async function runAgent(input: string) {
  const plan = createPlan(input);

  plan.status = "running";

  eventBus.emit("agent:step", {
    type: "plan_created",
    plan,
  });

  const results: AgentExecutionResult[] = [];

  for (const step of plan.steps) {
    try {
      step.status = "running";

      eventBus.emit("agent:step", {
        step: step.action,
        status: "running",
      });

      let result: unknown = null;

      // -------------------------
      // TOOL ROUTING
      // -------------------------

      if ("tool" in step && step.tool === "router") {
        result = {
          message: `Routing to: ${"input" in step ? step.input : step.action}`,
        };
      }

      if (step.action === "analyze_system") {
        result = await runTool("time");
      }

      if (step.action === "suggest_improvements") {
        result = {
          suggestion: "Optimize memory + reduce UI rerenders",
        };
      }

      if (step.action === "apply_plan") {
        result = {
          applied: true,
        };
      }

      if (step.action === "interpret") {
        result = {
          message: "Interpreting input...",
        };
      }

      step.status = "done";

      eventBus.emit("agent:step", {
        step: step.action,
        status: "done",
        result,
      });

      results.push({
        step: step.action,
        result,
      });
    } catch (err) {
      step.status = "failed";

      eventBus.emit("agent:step", {
        step: step.action,
        status: "failed",
        error: String(err),
      });

      results.push({
        step: step.action,
        error: String(err),
      });
    }
  }

  plan.status = "completed";

  eventBus.emit("agent:done", {
    plan,
    results,
  });

  return {
    plan,
    results,
  };
}
