"use client";

import { appRegistry } from "@/lib/apps/appRegistry";

type Props = {
  appId: string;
};

export default function OSWindowRenderer({ appId }: Props) {
  const app = appRegistry.get(appId);

  if (!app) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-white/40">
        Unknown application: {appId}
      </div>
    );
  }

  const Component = app.component;

  return (
    <div className="h-full w-full overflow-auto">
      <Component />
    </div>
  );
}