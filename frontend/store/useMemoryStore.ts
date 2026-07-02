import { create } from "zustand";

export type MemoryItem = {
  id: string;
  content: string;
  type: "command" | "navigation" | "note";
  timestamp: number;
};

type MemoryState = {
  memories: MemoryItem[];

  addMemory: (item: MemoryItem) => void;
  clearMemory: () => void;
  removeMemory: (id: string) => void;
};

export const useMemoryStore = create<MemoryState>((set) => ({
  memories: [],

  addMemory: (item) =>
    set((state) => ({
      memories: [item, ...state.memories].slice(0, 100),
    })),

  clearMemory: () =>
    set(() => ({
      memories: [],
    })),

  removeMemory: (id) =>
    set((state) => ({
      memories: state.memories.filter((m) => m.id !== id),
    })),
}));