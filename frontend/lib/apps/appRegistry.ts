import { ComponentType } from "react";

export interface RavandApp {
  id: string;

  title: string;

  icon?: string;

  route?: string;

  component: ComponentType<any>;

  defaultWidth: number;

  defaultHeight: number;

  resizable?: boolean;

  minimizable?: boolean;

  maximizable?: boolean;
}

class AppRegistry {
  private apps = new Map<string, RavandApp>();

  register(app: RavandApp) {
    this.apps.set(app.id, app);
  }

  unregister(id: string) {
    this.apps.delete(id);
  }

  get(id: string) {
    return this.apps.get(id);
  }

  getAll() {
    return Array.from(this.apps.values());
  }

  findByRoute(route: string) {
    return this.getAll().find((a) => a.route === route);
  }

  exists(id: string) {
    return this.apps.has(id);
  }

  clear() {
    this.apps.clear();
  }
}

export const appRegistry = new AppRegistry();