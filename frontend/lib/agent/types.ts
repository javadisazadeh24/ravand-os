export type AgentStep = {
  id: string;
  action: string;
  target?: string;
  status: "pending" | "running" | "done" | "failed";
};

export type AgentPlan = {
  id: string;
  originalInput: string;
  steps: AgentStep[];
  status: "created" | "running" | "completed" | "failed";
};