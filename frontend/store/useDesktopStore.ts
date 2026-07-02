import { create } from "zustand";

export type WindowState = {
  id: string;
  appId: string;

  title: string;

  x: number;
  y: number;

  width: number;
  height: number;

  zIndex: number;

  minimized: boolean;
  maximized: boolean;
  focused: boolean;
};

type DesktopStore = {
  windows: WindowState[];

  focusedWindowId: string | null;

  openWindow: (
    window: Omit<WindowState, "zIndex" | "focused">
  ) => void;

  closeWindow: (id: string) => void;

  focusWindow: (id: string) => void;

  moveWindow: (
    id: string,
    x: number,
    y: number
  ) => void;

  resizeWindow: (
    id: string,
    width: number,
    height: number
  ) => void;

  minimizeWindow: (id: string) => void;

  maximizeWindow: (id: string) => void;
};

export const useDesktopStore = create<DesktopStore>((set, get) => ({
  windows: [],

  focusedWindowId: null,

  openWindow(window) {
    const highest =
      Math.max(
        0,
        ...get().windows.map((w) => w.zIndex)
      ) + 1;

    set((state) => ({
      focusedWindowId: window.id,

      windows: [
        ...state.windows.map((w) => ({
          ...w,
          focused: false,
        })),
        {
          ...window,
          zIndex: highest,
          focused: true,
        },
      ],
    }));
  },

  closeWindow(id) {
    set((state) => ({
      windows: state.windows.filter((w) => w.id !== id),

      focusedWindowId:
        state.focusedWindowId === id
          ? null
          : state.focusedWindowId,
    }));
  },

  focusWindow(id) {
    const highest =
      Math.max(
        0,
        ...get().windows.map((w) => w.zIndex)
      ) + 1;

    set((state) => ({
      focusedWindowId: id,

      windows: state.windows.map((w) =>
        w.id === id
          ? {
              ...w,
              focused: true,
              zIndex: highest,
            }
          : {
              ...w,
              focused: false,
            }
      ),
    }));
  },

  moveWindow(id, x, y) {
    set((state) => ({
      windows: state.windows.map((w) =>
        w.id === id
          ? {
              ...w,
              x,
              y,
            }
          : w
      ),
    }));
  },

  resizeWindow(id, width, height) {
    set((state) => ({
      windows: state.windows.map((w) =>
        w.id === id
          ? {
              ...w,
              width,
              height,
            }
          : w
      ),
    }));
  },

  minimizeWindow(id) {
    set((state) => ({
      windows: state.windows.map((w) =>
        w.id === id
          ? {
              ...w,
              minimized: !w.minimized,
            }
          : w
      ),
    }));
  },

  maximizeWindow(id) {
    set((state) => ({
      windows: state.windows.map((w) =>
        w.id === id
          ? {
              ...w,
              maximized: !w.maximized,
            }
          : w
      ),
    }));
  },
}));