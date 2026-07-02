"use client";

import type { CSSProperties, ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";

import Sidebar from "@/components/sidebar/Sidebar";
import { useLayoutStore } from "@/store/useLayoutStore";
import { theme } from "@/styles/theme";
import Header from "./Header";
import MainContent from "./MainContent";
import StatusBar from "./StatusBar";

type AppShellProps = {
    children: ReactNode;
};

const shellThemeVars = {
    "--ravand-background": theme.colors.background,
    "--ravand-surface": theme.colors.surface,
    "--ravand-surface-2": theme.colors.surface2,
    "--ravand-border": theme.colors.border,
    "--ravand-primary": theme.colors.primary,
    "--ravand-secondary": theme.colors.secondary,
    "--ravand-success": theme.colors.success,
    "--ravand-warning": theme.colors.warning,
    "--ravand-danger": theme.colors.danger,
    "--ravand-text": theme.colors.text,
    "--ravand-muted": theme.colors.muted,
    "--ravand-radius-sm": theme.radius.sm,
    "--ravand-radius-md": theme.radius.md,
    "--ravand-radius-lg": theme.radius.lg,
    "--ravand-radius-xl": theme.radius.xl,
} as CSSProperties;

export default function AppShell({ children }: AppShellProps) {
    const isMobileSidebarOpen = useLayoutStore(
        (state) => state.isMobileSidebarOpen,
    );
    const closeMobileSidebar = useLayoutStore(
        (state) => state.closeMobileSidebar,
    );

    return (
        <div
            style={shellThemeVars}
            className="min-h-screen overflow-hidden bg-[var(--ravand-background)] text-[var(--ravand-text)]"
        >
            <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_18%_12%,rgba(99,102,241,0.18),transparent_32%),radial-gradient(circle_at_84%_10%,rgba(34,197,94,0.10),transparent_28%),linear-gradient(135deg,rgba(255,255,255,0.04),transparent_42%)]" />

            <div className="relative flex min-h-screen">
                <div className="hidden lg:block">
                    <Sidebar />
                </div>

                <AnimatePresence>
                    {isMobileSidebarOpen ? (
                        <motion.div
                            className="fixed inset-0 z-40 lg:hidden"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.18 }}
                        >
                            <button
                                type="button"
                                aria-label="Close navigation"
                                className="absolute inset-0 bg-black/55 backdrop-blur-sm"
                                onClick={closeMobileSidebar}
                            />
                            <Sidebar isMobile />
                        </motion.div>
                    ) : null}
                </AnimatePresence>

                <motion.div
                    className="flex min-w-0 flex-1 flex-col"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, ease: "easeOut" }}
                >
                    <Header />
                    <MainContent>{children}</MainContent>
                    <StatusBar />
                </motion.div>
            </div>
        </div>
    );
}
