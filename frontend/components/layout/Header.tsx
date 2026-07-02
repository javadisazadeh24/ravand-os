"use client";

import { ChevronLeft, ChevronRight, Menu, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

import { useLayoutStore } from "@/store/useLayoutStore";

export default function Header() {
    const isSidebarCollapsed = useLayoutStore(
        (state) => state.isSidebarCollapsed,
    );
    const toggleSidebar = useLayoutStore((state) => state.toggleSidebar);
    const toggleMobileSidebar = useLayoutStore(
        (state) => state.toggleMobileSidebar,
    );
    const DesktopToggleIcon = isSidebarCollapsed ? ChevronRight : ChevronLeft;

    return (
        <motion.header
            className="sticky top-0 z-30 flex h-16 shrink-0 items-center gap-3 border-b border-[var(--ravand-border)] bg-[rgba(17,17,17,0.74)] px-4 backdrop-blur-2xl sm:px-6"
            initial={{ y: -16, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.28, ease: "easeOut" }}
        >
            <button
                type="button"
                aria-label="Open navigation"
                className="grid size-10 place-items-center rounded-[var(--ravand-radius-sm)] border border-white/10 bg-white/[0.04] text-[var(--ravand-muted)] transition hover:border-white/20 hover:text-[var(--ravand-text)] lg:hidden"
                onClick={toggleMobileSidebar}
            >
                <Menu size={19} />
            </button>

            <button
                type="button"
                aria-label={
                    isSidebarCollapsed
                        ? "Expand navigation"
                        : "Collapse navigation"
                }
                className="hidden size-10 place-items-center rounded-[var(--ravand-radius-sm)] border border-white/10 bg-white/[0.04] text-[var(--ravand-muted)] transition hover:border-white/20 hover:text-[var(--ravand-text)] lg:grid"
                onClick={toggleSidebar}
            >
                <DesktopToggleIcon size={19} />
            </button>

            <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.16em] text-[var(--ravand-muted)]">
                    <Sparkles size={14} className="text-[var(--ravand-primary)]" />
                    Workspace
                </div>
                <h1 className="truncate text-sm font-semibold text-[var(--ravand-text)] sm:text-base">
                    RAVAND OS Control Surface
                </h1>
            </div>

            <div className="hidden items-center gap-2 rounded-[var(--ravand-radius-md)] border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-medium text-[var(--ravand-muted)] shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] sm:flex">
                <span className="size-2 rounded-full bg-[var(--ravand-success)] shadow-[0_0_16px_rgba(34,197,94,0.55)]" />
                <span className="truncate">Ready</span>
            </div>
        </motion.header>
    );
}
