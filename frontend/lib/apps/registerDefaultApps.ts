import { useAppStore } from "@/store/useAppStore";

export function registerDefaultApps() {
  const store = useAppStore.getState();

  store.registerApp({
    id: "chat",
    title: "Chat",
    icon: "💬",
    route: "/chat",
    defaultWidth: 900,
    defaultHeight: 650,
    multiple: true,
    showInDock: true,
  });

  store.registerApp({
    id: "dashboard",
    title: "Dashboard",
    icon: "📊",
    route: "/",
    defaultWidth: 1100,
    defaultHeight: 700,
    multiple: false,
    showInDock: true,
  });

  store.registerApp({
    id: "agents",
    title: "Agents",
    icon: "🤖",
    route: "/agents",
    defaultWidth: 900,
    defaultHeight: 600,
    multiple: true,
    showInDock: true,
  });

  store.registerApp({
    id: "memory",
    title: "Memory",
    icon: "🧠",
    route: "/memory",
    defaultWidth: 800,
    defaultHeight: 600,
    multiple: false,
    showInDock: true,
  });

  store.registerApp({
    id: "plugins",
    title: "Plugins",
    icon: "🧩",
    route: "/plugins",
    defaultWidth: 900,
    defaultHeight: 600,
    multiple: false,
    showInDock: true,
  });

  store.registerApp({
    id: "settings",
    title: "Settings",
    icon: "⚙️",
    route: "/settings",
    defaultWidth: 800,
    defaultHeight: 600,
    multiple: false,
    showInDock: true,
  });
}