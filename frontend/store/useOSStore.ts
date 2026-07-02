import { create } from "zustand";

type Command = {
  input: string;
  timestamp: number;
  type: "navigation" | "action" | "unknown";
};

type OSState = {
  activeRoute: string;
  history: Command[];

  setActiveRoute: (route: string) => void;
  pushCommand: (cmd: Command) => void;
  clearHistory: () => void;
};

export const useOSStore = create<OSState>((set) => ({
  activeRoute: "/",

  history: [],

  setActiveRoute: (route) =>
    set(() => ({
      activeRoute: route,
    })),

  pushCommand: (cmd) =>
    set((state) => ({
      history: [cmd, ...state.history].slice(0, 50),
    })),

  clearHistory: () =>
    set(() => ({
      history: [],
    })),
}));