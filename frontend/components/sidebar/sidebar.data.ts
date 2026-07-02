import {
    LayoutDashboard,
    MessageSquare,
    Bot,
    Puzzle,
    Brain,
    Settings,
    type LucideIcon,
} from "lucide-react";

export type SidebarItemData = {
    title: string;
    href: string;
    icon: LucideIcon;
    section: "Core" | "Intelligence" | "System";
    cmd?: string;
};

export const sidebarItems = [

    {
        title: "Dashboard",
        href: "/",
        icon: LayoutDashboard,
        section: "Core",
        cmd: "/dashboard",
    },

    {
        title: "Chat",
        href: "/chat",
        icon: MessageSquare,
        section: "Core",
        cmd: "/chat",
    },

    {
        title: "Agents",
        href: "/agents",
        icon: Bot,
        section: "Intelligence",
        cmd: "/agents",
    },

    {
        title: "Plugins",
        href: "/plugins",
        icon: Puzzle,
        section: "Intelligence",
    },

    {
        title: "Memory",
        href: "/memory",
        icon: Brain,
        section: "Intelligence",
    },

    {
        title: "Settings",
        href: "/settings",
        icon: Settings,
        section: "System",
    },

] satisfies SidebarItemData[];
