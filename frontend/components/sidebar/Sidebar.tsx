"use client";

import { motion } from "framer-motion";

import { cn } from "@/lib/utils";
import { useLayoutStore } from "@/store/useLayoutStore";
import { useOSCommand } from "@/lib/useOSCommand";

import SidebarFooter from "./SidebarFooter";
import SidebarHeader from "./SidebarHeader";
import SidebarItem from "./SidebarItem";
import { sidebarItems } from "./sidebar.data";

type SidebarProps = {
  isMobile?: boolean;
};

const expandedWidth = 288;
const collapsedWidth = 88;

export default function Sidebar({ isMobile = false }: SidebarProps) {
  const isSidebarCollapsed = useLayoutStore(
    (state) => state.isSidebarCollapsed
  );

  const closeMobileSidebar = useLayoutStore(
    (state) => state.closeMobileSidebar
  );

  const { execute } = useOSCommand();

  const isCollapsed = !isMobile && isSidebarCollapsed;

  /**
   * OS-level navigation handler
   * Sidebar is now a command surface (not UI-only)
   */
  const handleNavigate = (cmd: string) => {
    execute(cmd);

    if (isMobile) {
      closeMobileSidebar();
    }
  };

  return (
    <motion.aside
      className={cn(
        "z-50 flex h-screen shrink-0 flex-col border-r border-[var(--ravand-border)] bg-[rgba(17,17,17,0.78)] shadow-[20px_0_80px_rgba(0,0,0,0.35)] backdrop-blur-2xl",
        isMobile && "absolute left-0 top-0 w-[min(20rem,86vw)]"
      )}
      initial={isMobile ? { x: -320 } : false}
      animate={{
        x: 0,
        width: isMobile
          ? "min(20rem, 86vw)"
          : isCollapsed
          ? collapsedWidth
          : expandedWidth,
      }}
      exit={isMobile ? { x: -320 } : undefined}
      transition={{ type: "spring", stiffness: 420, damping: 36 }}
    >
      {/* Header */}
      <SidebarHeader isCollapsed={isCollapsed} isMobile={isMobile} />

      {/* Navigation */}
      <nav className="flex-1 space-y-1.5 overflow-y-auto px-3 py-4">
        {sidebarItems.map((item) => (
          <SidebarItem
            key={item.href}
            item={item}
            isCollapsed={isCollapsed}
            onNavigate={() => handleNavigate(item.cmd ?? item.href)}
          />
        ))}
      </nav>

      {/* Footer */}
      <SidebarFooter isCollapsed={isCollapsed} />
    </motion.aside>
  );
}