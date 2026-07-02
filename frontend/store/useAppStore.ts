import { create } from "zustand";
import { appRegistry, RavandApp } from "@/lib/apps/appRegistry";

type AppStore = {
  registerApp: (app: RavandApp) => void;

  unregisterApp: (id: string) => void;

  getApp: (id: string) => RavandApp | undefined;

  getApps: () => RavandApp[];
};

export const useAppStore = create<AppStore>(() => ({
  registerApp(app) {
    appRegistry.register(app);
  },

  unregisterApp(id) {
    appRegistry.unregister(id);
  },

  getApp(id) {
    return appRegistry.get(id);
  },

  getApps() {
    return appRegistry.getAll();
  },
}));