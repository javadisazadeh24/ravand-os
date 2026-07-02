import { create } from "zustand";
import { AppDefinition } from "@/types/app";

type AppStore = {
  apps: AppDefinition[];

  registerApp: (app: AppDefinition) => void;

  getApp: (id: string) => AppDefinition | undefined;
};

export const useAppStore = create<AppStore>((set, get) => ({
  apps: [],

  registerApp: (app) =>
    set((state) => ({
      apps: [...state.apps, app],
    })),

  getApp: (id) => {
    return get().apps.find((a) => a.id === id);
  },
}));