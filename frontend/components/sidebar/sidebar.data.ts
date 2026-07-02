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
};

export const sidebarItems = [

    {
        title: "Dashboard",
        href: "/",
        icon: LayoutDashboard,
    },

    {
        title: "Chat",
        href: "/chat",
        icon: MessageSquare,
    },

    {
        title: "Agents",
        href: "/agents",
        icon: Bot,
    },

    {
        title: "Plugins",
        href: "/plugins",
        icon: Puzzle,
    },

    {
        title: "Memory",
        href: "/memory",
        icon: Brain,
    },

    {
        title: "Settings",
        href: "/settings",
        icon: Settings,
    },

] satisfies SidebarItemData[];
