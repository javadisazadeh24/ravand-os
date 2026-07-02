"use client";

import {
    Bell,
    ChevronLeft,
    ChevronRight,
    Command,
    Menu,
    Plus,
    Settings,
    Sparkles,
    UserRound,
} from "lucide-react";
import { motion } from "framer-motion";
import { useState } from "react";

import { useLayoutStore } from "@/store/useLayoutStore";
import { useOSCommand } from "@/lib/useOSCommand";

export default function Header() {
    const isSidebarCollapsed = useLayoutStore(
        (state) => state.isSidebarCollapsed,
    );
    const toggleSidebar = useLayoutStore((state) => state.toggleSidebar);
    const toggleMobileSidebar = useLayoutStore(
        (state) => state.toggleMobileSidebar,
    );
    const { execute } = useOSCommand();
    const [command, setCommand] = useState("");
    const DesktopToggleIcon = isSidebarCollapsed ? ChevronRight : ChevronLeft;

    const submitCommand = () => {
        if (!command.trim()) return;
        execute(command);
        setCommand("");
    };

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

            <div className="hidden min-w-0 flex-1 sm:block">
                <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.16em] text-[var(--ravand-muted)]">
                    <Sparkles size={14} className="text-[var(--ravand-primary)]" />
                    Workspace
                </div>
                <h1 className="truncate text-sm font-semibold text-[var(--ravand-text)] sm:text-base">
                    RAVAND OS Control Surface
                </h1>
            </div>

            <div className="flex h-11 min-w-0 flex-1 items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.065] px-3 text-sm text-white/55 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)] sm:max-w-xl">
                <Command size={16} className="shrink-0" />
                <input
                    value={command}
                    onChange={(event) => setCommand(event.target.value)}
                    onKeyDown={(event) => {
                        if (event.key === "Enter") submitCommand();
                    }}
                    placeholder="Command Ravand..."
                    className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-white/35"
                />
                <kbd className="hidden rounded-md border border-white/10 bg-white/5 px-1.5 py-0.5 text-[10px] text-white/35 md:block">
                    Enter
                </kbd>
            </div>

            <div className="flex items-center gap-2">
                {[Plus, Bell, Settings, UserRound].map((Icon, index) => (
                    <motion.button
                        key={index}
                        type="button"
                        className="grid size-10 place-items-center rounded-2xl border border-white/10 bg-white/[0.04] text-white/55 transition hover:text-white"
                        whileHover={{ y: -2, scale: 1.03 }}
                        whileTap={{ scale: 0.96 }}
                    >
                        <Icon size={17} />
                    </motion.button>
                ))}
            </div>
        </motion.header>
    );
}
