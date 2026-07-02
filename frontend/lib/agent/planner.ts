import { eventBus } from "../core/eventBus";

/**
 * 🧠 RAVAND OS — Planner Engine (FINAL)
 * Converts natural language → structured execution plan
 */

export type PlanStep = {
  id: string;
  action: string;
  input?: string;
  status: "pending" | "running" | "done" | "failed";
};

export type Plan = {
  id: string;
  originalInput: string;
  goal: string;
  steps: PlanStep[];
  status: "created" | "running" | "completed" | "failed";
};

/**
 * Generate unique ID
 */
function uid() {
  return crypto.randomUUID();
}

/**
 * 🧠 CORE PLANNER
 * Converts input → structured plan
 */
export function createPlan(input: string): Plan {
  const normalized = input.toLowerCase();

  const plan: Plan = {
    id: uid(),
    originalInput: input,
    goal: inferGoal(normalized),
    steps: [],
    status: "created",
  };

  /**
   * STEP GENERATION RULES
   */

  // -------------------------
  // SYSTEM OPTIMIZATION TASKS
  // -------------------------
  if (normalized.includes("optimize")) {
    plan.steps.push(
      makeStep("interpret", "Analyze system state"),
      makeStep("scan", "Scan performance bottlenecks"),
      makeStep("suggest_improvements", "Generate optimization plan"),
      makeStep("apply_plan", "Apply system improvements")
    );
  }

  // -------------------------
  // DASHBOARD / UI TASKS
  // -------------------------
  else if (normalized.includes("dashboard")) {
    plan.steps.push(
      makeStep("interpret", "Interpret UI request"),
      makeStep("navigate", "/dashboard"),
      makeStep("render", "Load dashboard components")
    );
  }

  // -------------------------
  // AGENT TASKS
  // -------------------------
  else if (normalized.includes("agent")) {
    plan.steps.push(
      makeStep("interpret", "Parse agent instruction"),
      makeStep("plan", "Generate execution strategy"),
      makeStep("execute", "Run agent workflow"),
      makeStep("finalize", "Return structured result")
    );
  }

  // -------------------------
  // DEFAULT GENERIC TASK
  // -------------------------
  else {
    plan.steps.push(
      makeStep("interpret", "Understand user request"),
      makeStep("decide", "Select best execution path"),
      makeStep("execute", "Perform action")
    );
  }

  /**
   * EVENT: PLAN CREATED
   */
  eventBus.emit("planner:created", plan);

  return plan;
}

/**
 * Create single step helper
 */
function makeStep(action: string, input?: string): PlanStep {
  return {
    id: uid(),
    action,
    input,
    status: "pending",
  };
}

/**
 * Infer goal from input (simple semantic layer)
 */
function inferGoal(input: string): string {
  if (input.includes("optimize")) return "System Optimization";
  if (input.includes("dashboard")) return "UI Navigation";
  if (input.includes("agent")) return "Agent Execution";
  return "General Task Execution";
}