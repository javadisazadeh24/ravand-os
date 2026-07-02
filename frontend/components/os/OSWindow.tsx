"use client";

import { useMemo } from "react";
import { useWindowStore } from "@/lib/runtime/windowStore";
import { appRegistry } from "@/lib/core/appRegistry";
import WindowHeader from "./WindowHeader";

export default function OSWindow({ windowId }: { windowId: string }) {
  const window = useWindowStore((s) =>
    s.windows.find((w) => w.id === windowId)
  );

  const actions = useWindowStore();

  const App = useMemo(() => {
    if (!window) return null;
    return appRegistry.getApp(window.appId)?.component;
  }, [window]);

  if (!window || !App) return null;

  return (
    <div
      className="flex flex-col h-full bg-black/70 border border-white/10 rounded-xl overflow-hidden"
      onMouseDown={() => actions.focusWindow(windowId)}
    >
      <WindowHeader
        windowId={windowId}
        title={window.title}
        position={window.position}
        size={window.size}
        isMaximized={window.isMaximized}
        onClose={() => actions.closeWindow(windowId)}
        onMinimize={() => actions.minimizeWindow(windowId)}
        onMaximize={() => actions.maximizeWindow(windowId)}
        onMove={actions.updatePosition}
        onResize={actions.updateSize}
      />

      <div className="flex-1 overflow-auto">
        <App />
      </div>
    </div>
  );
}