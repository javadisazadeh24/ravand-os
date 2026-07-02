"use client";

import { useCallback } from "react";

import { aiBrain } from "@/lib/ai/aiBrain";
import { launchWindow } from "@/lib/window/windowLauncher";

export function useCommandRouter() {
  const execute = useCallback(async (input: string) => {
    const result = await aiBrain(input);

    // -------------------------
    // WINDOW LAUNCHING LAYER
    // -------------------------
    if (result.intent === "navigation" && result.target) {
      const appId = result.target.replace("/", "");

      launchWindow({ appId });

      return {
        success: true,
        mode: "window",
        response: `Opened ${appId} window`,
      };
    }

    // -------------------------
    // NORMAL RESPONSE
    // -------------------------
    return {
      success: true,
      mode: "response",
      response: result.response ?? "",
    };
  }, []);

  return {
    execute,
  };
}