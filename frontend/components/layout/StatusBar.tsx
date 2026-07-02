"use client";

import { Activity, CircleCheck, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

const statusItems = [
    {
        label: "Shell",
        value: "Ready",
        icon: CircleCheck,
        tone: "text-[var(--ravand-success)]",
    },
    {
        label: "Layout",
        value: "Responsive",
        icon: Activity,
        tone: "text-[var(--ravand-primary)]",
    },
    {
        label: "Theme",
        value: "Applied",
        icon: ShieldCheck,
        tone: "text-[var(--ravand-warning)]",
    },
] as const;

export default function StatusBar() {
    return (
        <motion.footer
            className="flex min-h-10 shrink-0 flex-wrap items-center justify-between gap-3 border-t border-[var(--ravand-border)] bg-[rgba(17,17,17,0.72)] px-4 py-2 text-xs text-[var(--ravand-muted)] backdrop-blur-2xl sm:px-6"
            initial={{ y: 14, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.28, ease: "easeOut", delay: 0.12 }}
        >
            <span className="font-medium text-[var(--ravand-text)]">
                RAVAND OS
            </span>

            <div className="flex flex-wrap items-center gap-3 sm:gap-5">
                {statusItems.map((item) => {
                    const Icon = item.icon;

                    return (
                        <div key={item.label} className="flex items-center gap-2">
                            <Icon size={14} className={item.tone} />
                            <span>{item.label}</span>
                            <span className="font-medium text-[var(--ravand-text)]">
                                {item.value}
                            </span>
                        </div>
                    );
                })}
            </div>
        </motion.footer>
    );
}
