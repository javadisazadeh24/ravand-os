"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Gauge, UserRound } from "lucide-react";

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
                <div className="relative grid size-9 shrink-0 place-items-center rounded-[var(--ravand-radius-sm)] bg-white/10 text-white">
                    <UserRound size={18} />
                    <span className="absolute -bottom-0.5 -right-0.5 size-2.5 rounded-full border border-[#111] bg-[var(--ravand-success)]" />
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
                                J. Isazadeh
                            </p>
                            <p className="truncate text-xs text-[var(--ravand-muted)]">
                                <Gauge size={12} className="mr-1 inline" />
                                Operator online
                            </p>
                        </motion.div>
                    ) : null}
                </AnimatePresence>
            </div>
        </div>
    );
}
