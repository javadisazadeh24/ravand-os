"use client";

import { useEffect } from "react";
import WindowManager from "./WindowManager";
import { eventBus } from "@/lib/core/eventBus";
import { appLauncher } from "@/lib/launcher/appLauncher";

export default function DesktopCanvas() {
  useEffect(() => {
    const onLaunch = (data: any) => {
      if (!data?.appId) return;

      appLauncher.launchApp(data.appId);
    };

    eventBus.on("app:launch:request", onLaunch);

    return () => {
      eventBus.off("app:launch:request", onLaunch);
    };
  }, []);

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      <WindowManager />
    </div>
  );
}