import { appRegistry } from "@/lib/apps/appRegistry";

// ⚠️ مهم: این‌ها باید REAL components باشند
import ChatPage from "@/app/chat/page";
import DashboardPage from "@/app/page";
import AgentsPage from "@/app/agents/page";
import MemoryPage from "@/app/memory/page";
import PluginsPage from "@/app/plugins/page";
import SettingsPage from "@/app/settings/page";

export function registerDefaultApps() {
  // -------------------------
  // CHAT APP
  // -------------------------
  appRegistry.register({
    id: "chat",
    title: "Chat",
    icon: "💬",
    route: "/chat",
    component: ChatPage,
    defaultWidth: 900,
    defaultHeight: 650,
    resizable: true,
    minimizable: true,
    maximizable: true,
  });

  // -------------------------
  // DASHBOARD
  // -------------------------
  appRegistry.register({
    id: "dashboard",
    title: "Dashboard",
    icon: "📊",
    route: "/",
    component: DashboardPage,
    defaultWidth: 1100,
    defaultHeight: 700,
    resizable: true,
    minimizable: true,
    maximizable: true,
  });

  // -------------------------
  // AGENTS
  // -------------------------
  appRegistry.register({
    id: "agents",
    title: "Agents",
    icon: "🤖",
    route: "/agents",
    component: AgentsPage,
    defaultWidth: 950,
    defaultHeight: 650,
    resizable: true,
    minimizable: true,
    maximizable: true,
  });

  // -------------------------
  // MEMORY
  // -------------------------
  appRegistry.register({
    id: "memory",
    title: "Memory",
    icon: "🧠",
    route: "/memory",
    component: MemoryPage,
    defaultWidth: 850,
    defaultHeight: 600,
    resizable: true,
    minimizable: true,
    maximizable: true,
  });

  // -------------------------
  // PLUGINS
  // -------------------------
  appRegistry.register({
    id: "plugins",
    title: "Plugins",
    icon: "🧩",
    route: "/plugins",
    component: PluginsPage,
    defaultWidth: 900,
    defaultHeight: 600,
    resizable: true,
    minimizable: true,
    maximizable: true,
  });

  // -------------------------
  // SETTINGS
  // -------------------------
  appRegistry.register({
    id: "settings",
    title: "Settings",
    icon: "⚙️",
    route: "/settings",
    component: SettingsPage,
    defaultWidth: 800,
    defaultHeight: 600,
    resizable: true,
    minimizable: true,
    maximizable: true,
  });
}