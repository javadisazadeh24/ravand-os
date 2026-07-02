export type ToolResult = {
  success: boolean;
  data?: any;
  error?: string;
};

export type ToolName = "time" | "echo" | "calc";

/**
 * 🧠 RAVAND OS — Tool Router
 * Central execution layer for all tools
 */

export async function runTool(
  tool: ToolName,
  input?: any
): Promise<ToolResult> {
  try {
    switch (tool) {
      /* -------------------------
         TIME TOOL
      -------------------------- */
      case "time": {
        return {
          success: true,
          data: new Date().toLocaleString(),
        };
      }

      /* -------------------------
         ECHO TOOL
      -------------------------- */
      case "echo": {
        return {
          success: true,
          data: input,
        };
      }

      /* -------------------------
         CALC TOOL
      -------------------------- */
      case "calc": {
        // ⚠️ simple safe eval (not production secure yet)
        const result = Function(`return (${input})`)();

        return {
          success: true,
          data: result,
        };
      }

      default:
        return {
          success: false,
          error: "Tool not found",
        };
    }
  } catch (err: any) {
    return {
      success: false,
      error: err.message,
    };
  }
}