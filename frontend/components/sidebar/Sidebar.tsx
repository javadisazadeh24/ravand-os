"use client";

import { motion } from "framer-motion";
import { Search } from "lucide-react";
import { useMemo, useState } from "react";

import { cn } from "@/lib/utils";
import { useLayoutStore } from "@/store/useLayoutStore";
import { useOSCommand } from "@/lib/useOSCommand";

import SidebarFooter from "./SidebarFooter";
import SidebarHeader from "./SidebarHeader";
import SidebarItem from "./SidebarItem";
import { sidebarItems, type SidebarItemData } from "./sidebar.data";

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
  const [query, setQuery] = useState("");

  const isCollapsed = !isMobile && isSidebarCollapsed;
  const sections = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    const filteredItems = sidebarItems.filter((item) =>
      item.title.toLowerCase().includes(normalizedQuery)
    );

    return filteredItems.reduce<Record<string, SidebarItemData[]>>(
      (groups, item) => {
        groups[item.section] = [...(groups[item.section] ?? []), item];
        return groups;
      },
      {}
    );
  }, [query]);

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

      {!isCollapsed ? (
        <div className="px-3 pt-3">
          <div className="flex h-10 items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.055] px-3 text-sm text-white/45 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
            <Search size={15} />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search OS"
              className="min-w-0 flex-1 bg-transparent text-white/80 outline-none placeholder:text-white/35"
            />
          </div>
        </div>
      ) : null}

      {/* Navigation */}
      <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-4">
        {Object.entries(sections).map(([section, items]) => (
          <div key={section} className="space-y-1.5">
            {!isCollapsed ? (
              <div className="px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-white/35">
                {section}
              </div>
            ) : null}

            {items.map((item) => (
              <SidebarItem
                key={item.href}
                item={item}
                isCollapsed={isCollapsed}
                onNavigate={() => handleNavigate(item.cmd ?? item.href)}
              />
            ))}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <SidebarFooter isCollapsed={isCollapsed} />
    </motion.aside>
  );
}
