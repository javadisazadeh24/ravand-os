"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Gauge } from "lucide-react";

import { cn } from "@/lib/utils";

type SidebarFooterProps = {
    isCollapsed: boolean;
};

export default function SidebarFooter({ isCollapsed }: SidebarFooterProps) {
    return (
        <div className="border-t border-[var(--ravand-border)] p-3">
            <div
                className={cn(
                    "flex items-center gap-3 rounded-[var(--ravand-radius-md)] border border-white/10 bg-white/[0.04] p-3",
                    isCollapsed && "justify-center px-2",
                )}
            >
                <div className="grid size-9 shrink-0 place-items-center rounded-[var(--ravand-radius-sm)] bg-[rgba(34,197,94,0.12)] text-[var(--ravand-success)]">
                    <Gauge size={18} />
                </div>

                <AnimatePresence initial={false}>
                    {!isCollapsed ? (
                        <motion.div
                            className="min-w-0"
                            initial={{ opacity: 0, x: -8 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -8 }}
                            transition={{ duration: 0.16 }}
                        >
                            <p className="truncate text-xs font-semibold text-[var(--ravand-text)]">
                                UI Framework
                            </p>
                            <p className="truncate text-xs text-[var(--ravand-muted)]">
                                Shell ready
                            </p>
                        </motion.div>
                    ) : null}
                </AnimatePresence>
            </div>
        </div>
    );
}
