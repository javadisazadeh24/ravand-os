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
import { useCommandRouter } from "@/hooks/useCommandRouter";

export default function Header() {
    const isSidebarCollapsed = useLayoutStore(
        (state) => state.isSidebarCollapsed,
    );
    const toggleSidebar = useLayoutStore((state) => state.toggleSidebar);
    const toggleMobileSidebar = useLayoutStore(
        (state) => state.toggleMobileSidebar,
    );

    const { execute } = useCommandRouter();

    const [command, setCommand] = useState("");

    const DesktopToggleIcon = isSidebarCollapsed
        ? ChevronRight
        : ChevronLeft;

    const submitCommand = async () => {
        if (!command.trim()) return;

        await execute(command);

        setCommand("");
    };

    return (
        <motion.header
            className="sticky top-0 z-30 flex h-16 shrink-0 items-center gap-3 border-b border-[var(--ravand-border)] bg-[rgba(17,17,17,0.74)] px-4 backdrop-blur-2xl sm:px-6"
            initial={{ y: -16, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.28, ease: "easeOut" }}
        >
            {/* Mobile Sidebar */}
            <button
                type="button"
                className="grid size-10 place-items-center rounded-xl border border-white/10 bg-white/5 text-white/60 lg:hidden"
                onClick={toggleMobileSidebar}
            >
                <Menu size={18} />
            </button>

            {/* Desktop Sidebar Toggle */}
            <button
                type="button"
                className="hidden size-10 place-items-center rounded-xl border border-white/10 bg-white/5 text-white/60 lg:grid"
                onClick={toggleSidebar}
            >
                <DesktopToggleIcon size={18} />
            </button>

            {/* Title */}
            <div className="hidden flex-1 sm:block">
                <div className="flex items-center gap-2 text-[11px] uppercase tracking-widest text-white/40">
                    <Sparkles size={13} className="text-indigo-400" />
                    Workspace
                </div>
                <h1 className="text-sm font-semibold text-white">
                    RAVAND OS Control Surface
                </h1>
            </div>

            {/* Command Input */}
            <div className="flex flex-1 items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2">
                <Command size={16} className="text-white/40" />

                <input
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") submitCommand();
                    }}
                    placeholder="Command Ravand..."
                    className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-white/30"
                />

                <kbd className="hidden rounded-md border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] text-white/40 md:block">
                    Enter
                </kbd>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
                {[Plus, Bell, Settings, UserRound].map((Icon, i) => (
                    <motion.button
                        key={i}
                        className="grid size-10 place-items-center rounded-xl border border-white/10 bg-white/5 text-white/60 hover:text-white"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <Icon size={16} />
                    </motion.button>
                ))}
            </div>
        </motion.header>
    );
}