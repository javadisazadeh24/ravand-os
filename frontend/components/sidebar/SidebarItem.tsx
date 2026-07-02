"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";

import { cn } from "@/lib/utils";
import type { SidebarItemData } from "./sidebar.data";

type SidebarItemProps = {
    item: SidebarItemData;
    isCollapsed: boolean;
    onNavigate?: () => void;
};

export default function SidebarItem({
    item,
    isCollapsed,
    onNavigate,
}: SidebarItemProps) {
    const pathname = usePathname();
    const Icon = item.icon;
    const isActive =
        item.href === "/" ? pathname === item.href : pathname.startsWith(item.href);

    return (
        <Link
            href={item.href}
            aria-label={isCollapsed ? item.title : undefined}
            title={isCollapsed ? item.title : undefined}
            onClick={onNavigate}
            className={cn(
                "group relative flex h-11 items-center gap-3 overflow-hidden rounded-[var(--ravand-radius-md)] px-3 text-sm font-medium transition",
                isCollapsed && "justify-center px-0",
                isActive
                    ? "text-[var(--ravand-text)]"
                    : "text-[var(--ravand-muted)] hover:text-[var(--ravand-text)]",
            )}
        >
            {isActive ? (
                <motion.span
                    layoutId="sidebar-active-item"
                    className="absolute inset-0 rounded-[var(--ravand-radius-md)] border border-white/10 bg-white/[0.08] shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]"
                    transition={{ type: "spring", stiffness: 520, damping: 42 }}
                />
            ) : (
                <span className="absolute inset-0 rounded-[var(--ravand-radius-md)] bg-white/[0.04] opacity-0 transition group-hover:opacity-100" />
            )}

            <span
                className={cn(
                    "relative z-10 grid size-8 shrink-0 place-items-center rounded-[var(--ravand-radius-sm)] transition",
                    isActive
                        ? "bg-[var(--ravand-primary)] text-white shadow-[0_10px_24px_rgba(99,102,241,0.28)]"
                        : "bg-white/[0.05] text-[var(--ravand-muted)] group-hover:text-[var(--ravand-text)]",
                )}
            >
                <Icon size={17} />
            </span>

            <AnimatePresence initial={false}>
                {!isCollapsed ? (
                    <motion.span
                        className="relative z-10 truncate"
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -8 }}
                        transition={{ duration: 0.16 }}
                    >
                        {item.title}
                    </motion.span>
                ) : null}
            </AnimatePresence>
        </Link>
    );
}
