import { tools } from "./tools";

export async function runTool(
  toolName: string,
  input?: any
) {
  const tool = tools[toolName];

  if (!tool) {
    return {
      success: false,
      error: `Tool not found: ${toolName}`,
    };
  }

  return await tool.execute(input);
}