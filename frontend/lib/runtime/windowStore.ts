import { create } from "zustand";
import { eventBus } from "@/lib/core/eventBus";

export interface WindowState {
  id: string;
  appId: string;
  title: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  zIndex: number;
  isMinimized: boolean;
  isMaximized: boolean;
}

interface WindowStore {
  windows: WindowState[];
  focusedWindowId: string | null;
  baseZIndex: number;

  openWindow: (
    appId: string,
    title: string,
    size?: { width: number; height: number }
  ) => string;

  closeWindow: (id: string) => void;
  focusWindow: (id: string) => void;
  updatePosition: (id: string, pos: { x: number; y: number }) => void;
  updateSize: (id: string, size: { width: number; height: number }) => void;
  minimizeWindow: (id: string) => void;
  maximizeWindow: (id: string) => void;
}

export const useWindowStore = create<WindowStore>((set, get) => ({
  windows: [],
  focusedWindowId: null,
  baseZIndex: 1000,

  openWindow: (appId, title, size = { width: 800, height: 600 }) => {
    const id = `win_${Date.now()}`;
    const { windows, baseZIndex } = get();

    const win: WindowState = {
      id,
      appId,
      title,
      position: { x: 80 + windows.length * 20, y: 80 + windows.length * 20 },
      size,
      zIndex: baseZIndex + 1,
      isMinimized: false,
      isMaximized: false,
    };

    set({
      windows: [...windows, win],
      focusedWindowId: id,
      baseZIndex: baseZIndex + 1,
    });

    eventBus.emit("window:opened", { id, appId });

    return id;
  },

  closeWindow: (id) => {
    set((state) => ({
      windows: state.windows.filter((w) => w.id !== id),
      focusedWindowId:
        state.focusedWindowId === id ? null : state.focusedWindowId,
    }));

    eventBus.emit("window:closed", { id });
  },

  focusWindow: (id) => {
    const { windows } = get();
    const maxZ = Math.max(...windows.map((w) => w.zIndex), 1000);

    set({
      windows: windows.map((w) =>
        w.id === id
          ? { ...w, zIndex: maxZ + 1, isMinimized: false }
          : w
      ),
      focusedWindowId: id,
      baseZIndex: maxZ + 1,
    });
  },

  updatePosition: (id, pos) =>
    set((s) => ({
      windows: s.windows.map((w) =>
        w.id === id ? { ...w, position: pos } : w
      ),
    })),

  updateSize: (id, size) =>
    set((s) => ({
      windows: s.windows.map((w) =>
        w.id === id ? { ...w, size } : w
      ),
    })),

  minimizeWindow: (id) =>
    set((s) => ({
      windows: s.windows.map((w) =>
        w.id === id ? { ...w, isMinimized: true } : w
      ),
    })),

  maximizeWindow: (id) =>
    set((s) => ({
      windows: s.windows.map((w) =>
        w.id === id
          ? { ...w, isMaximized: !w.isMaximized }
          : w
      ),
    })),
}));