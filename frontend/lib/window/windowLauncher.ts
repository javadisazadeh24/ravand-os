import { useDesktopStore } from "@/store/useDesktopStore";
import { useAppStore } from "@/store/useAppStore";

type LaunchOptions = {
  appId: string;
  instanceId?: string;
};

export function launchWindow({ appId }: LaunchOptions) {
  const app = useAppStore.getState().getApp(appId);
  const desktop = useDesktopStore.getState();

  if (!app) {
    console.warn(`App not found: ${appId}`);
    return;
  }

  desktop.openWindow({
    id: crypto.randomUUID(),
    appId: app.id,
    title: app.title,

    x: 120 + Math.random() * 80,
    y: 80 + Math.random() * 60,

    width: app.defaultWidth,
    height: app.defaultHeight,

    minimized: false,
    maximized: false,
  });
}