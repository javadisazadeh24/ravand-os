export type AppDefinition = {
  id: string;
  title: string;
  icon: string;
  route: string;

  defaultWidth: number;
  defaultHeight: number;

  multiple: boolean;
  showInDock: boolean;

  component?: React.ComponentType<any>;
};

class AppRegistry {
  private apps: Map<string, AppDefinition> = new Map();

  registerApp(app: AppDefinition) {
    this.apps.set(app.id, app);
  }

  getApp(id: string) {
    return this.apps.get(id);
  }

  getAllApps() {
    return Array.from(this.apps.values());
  }

  getDockApps() {
    return this.getAllApps().filter((a) => a.showInDock);
  }
}

export const appRegistry = new AppRegistry();