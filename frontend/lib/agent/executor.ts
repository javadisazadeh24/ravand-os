import { AgentPlan } from "./types";

/**
 * Executes agent plan step-by-step
 */
export async function executePlan(plan: AgentPlan): Promise<AgentPlan> {
  plan.status = "running";

  for (const step of plan.steps) {
    step.status = "running";

    await new Promise((r) => setTimeout(r, 300)); // simulate execution

    try {
      switch (step.action) {
        case "navigate":
          console.log("Navigating to:", step.target);
          break;

        case "fetch_data":
          console.log("Fetching data...");
          break;

        case "interpret":
          console.log("Interpreting input...");
          break;

        default:
          console.log("Unknown step");
      }

      step.status = "done";
    } catch (e) {
      step.status = "failed";
    }
  }

  plan.status = "completed";

  return plan;
}