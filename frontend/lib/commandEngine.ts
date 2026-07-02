export type CommandResult = {
  type: "navigation" | "action" | "unknown";
  target?: string;
  payload?: any;
  message?: string;
};

export function parseCommand(input: string): CommandResult {
  const text = input.trim().toLowerCase();

  // NAVIGATION COMMANDS
  if (text === "/chat") {
    return { type: "navigation", target: "/chat" };
  }

  if (text === "/dashboard") {
    return { type: "navigation", target: "/" };
  }

  if (text === "/agents") {
    return { type: "navigation", target: "/agents" };
  }

  if (text === "/plugins") {
    return { type: "navigation", target: "/plugins" };
  }

  if (text === "/settings") {
    return { type: "navigation", target: "/settings" };
  }

  // SYSTEM ACTIONS
  if (text.startsWith("/echo ")) {
    return {
      type: "action",
      message: text.replace("/echo ", "")
    };
  }

  // UNKNOWN
  return {
    type: "unknown",
    message: input
  };
}