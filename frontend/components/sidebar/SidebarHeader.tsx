"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ChevronsUpDown, Cpu, X } from "lucide-react";

import { cn } from "@/lib/utils";
import { useLayoutStore } from "@/store/useLayoutStore";

type SidebarHeaderProps = {
    isCollapsed: boolean;
    isMobile?: boolean;
};

export default function SidebarHeader({
    isCollapsed,
    isMobile = false,
}: SidebarHeaderProps) {
    const closeMobileSidebar = useLayoutStore(
        (state) => state.closeMobileSidebar,
    );

    return (
        <div
            className={cn(
                "flex h-16 shrink-0 items-center border-b border-[var(--ravand-border)] px-4",
                isCollapsed ? "justify-center" : "justify-between",
            )}
        >
            <div className="flex min-w-0 items-center gap-3">
                <div className="grid size-10 shrink-0 place-items-center rounded-[var(--ravand-radius-md)] border border-white/10 bg-[linear-gradient(135deg,var(--ravand-primary),var(--ravand-secondary))] text-white shadow-[0_12px_30px_rgba(99,102,241,0.28)]">
                    <Cpu size={20} />
                </div>

                <AnimatePresence initial={false}>
                    {!isCollapsed ? (
                        <motion.div
                            className="min-w-0"
                            initial={{ opacity: 0, x: -8 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -8 }}
                            transition={{ duration: 0.18 }}
                        >
                            <div className="flex items-center gap-1.5">
                                <p className="truncate text-sm font-bold">
                                    Ravand Prime
                                </p>
                                <ChevronsUpDown size={13} className="text-white/40" />
                            </div>
                            <p className="truncate text-xs text-[var(--ravand-muted)]">
                                Personal AI workspace
                            </p>
                        </motion.div>
                    ) : null}
                </AnimatePresence>
            </div>

            {isMobile ? (
                <button
                    type="button"
                    aria-label="Close navigation"
                    className="grid size-9 place-items-center rounded-[var(--ravand-radius-sm)] border border-white/10 bg-white/[0.04] text-[var(--ravand-muted)] transition hover:text-[var(--ravand-text)]"
                    onClick={closeMobileSidebar}
                >
                    <X size={18} />
                </button>
            ) : null}
        </div>
    );
}
