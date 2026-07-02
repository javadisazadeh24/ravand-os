export type ToolResult = {
  success: boolean;
  data?: any;
  error?: string;
};

export type Tool = {
  name: string;
  description: string;
  execute: (input: any) => Promise<ToolResult> | ToolResult;
};

/**
 * 🧠 Simple Tool Registry
 */
export const tools: Record<string, Tool> = {
  echo: {
    name: "echo",
    description: "Returns input back",
    execute: async (input) => {
      return {
        success: true,
        data: input,
      };
    },
  },

  time: {
    name: "time",
    description: "Returns current server time",
    execute: async () => {
      return {
        success: true,
        data: new Date().toISOString(),
      };
    },
  },

  calc: {
    name: "calc",
    description: "Simple math evaluator",
    execute: async (input: string) => {
      try {
        // ⚠️ safe enough for demo, later sandbox می‌کنیم
        const result = Function(`return (${input})`)();
        return {
          success: true,
          data: result,
        };
      } catch (e) {
        return {
          success: false,
          error: "Invalid expression",
        };
      }
    },
  },
};