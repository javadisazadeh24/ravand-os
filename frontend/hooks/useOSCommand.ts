"use client";

import { useCallback } from "react";

import { aiBrain } from "@/lib/ai/aiBrain";
import { useDesktopStore } from "@/store/useDesktopStore";
import { useAppStore } from "@/store/useAppStore";

export function useOSCommand() {
  const openWindow = useDesktopStore((s) => s.openWindow);
  const getApp = useAppStore((s) => s.getApp);

  const execute = useCallback(async (input: string) => {
    const result = await aiBrain(input);

    // Navigation → Open Window
    if (result.intent === "navigation" && result.target) {
      const route = result.target;

      const app = useAppStore
        .getState()
        .apps.find((a) => a.route === route);

      if (app) {
        openWindow({
          id: crypto.randomUUID(),
          appId: app.id,
          title: app.title,

          x: 120,
          y: 80,

          width: app.defaultWidth,
          height: app.defaultHeight,

          minimized: false,
          maximized: false,
        });

        return {
          success: true,
          response: `Opened ${app.title}`,
        };
      }

      return {
        success: false,
        response: `Application not found for route ${route}`,
      };
    }

    return {
      success: true,
      response: result.response ?? "",
    };
  }, [openWindow, getApp]);

  return {
    execute,
  };
}