export type AppDefinition = {
  id: string;
  title: string;
  icon: string;
  route: string;

  defaultWidth: number;
  defaultHeight: number;

  multiple: boolean; // can open multiple windows?

  showInDock: boolean;
};