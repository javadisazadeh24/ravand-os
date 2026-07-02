import { ToolName } from "./toolRouter";

export type ToolDefinition = {
  name: ToolName;
  description: string;
  category: "system" | "math" | "io";
};

export const toolRegistry: ToolDefinition[] = [
  {
    name: "time",
    description: "Get current system time",
    category: "system",
  },
  {
    name: "echo",
    description: "Return input as output",
    category: "io",
  },
  {
    name: "calc",
    description: "Simple math evaluation",
    category: "math",
  },
];