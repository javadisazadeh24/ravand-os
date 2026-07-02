"use client";

import { create } from "zustand";

type LayoutState = {
    isSidebarCollapsed: boolean;
    isMobileSidebarOpen: boolean;
    collapseSidebar: () => void;
    expandSidebar: () => void;
    toggleSidebar: () => void;
    openMobileSidebar: () => void;
    closeMobileSidebar: () => void;
    toggleMobileSidebar: () => void;
};

export const useLayoutStore = create<LayoutState>((set) => ({
    isSidebarCollapsed: false,
    isMobileSidebarOpen: false,
    collapseSidebar: () => set({ isSidebarCollapsed: true }),
    expandSidebar: () => set({ isSidebarCollapsed: false }),
    toggleSidebar: () =>
        set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),
    openMobileSidebar: () => set({ isMobileSidebarOpen: true }),
    closeMobileSidebar: () => set({ isMobileSidebarOpen: false }),
    toggleMobileSidebar: () =>
        set((state) => ({ isMobileSidebarOpen: !state.isMobileSidebarOpen })),
}));
