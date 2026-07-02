"use client";

import { useWindowStore } from "@/lib/runtime/windowStore";
import OSWindow from "./OSWindow";

export default function WindowManager() {
  const windows = useWindowStore((s) => s.windows);

  return (
    <div className="absolute inset-0">
      {windows.map((w) => (
        <div
          key={w.id}
          style={{
            position: "absolute",
            left: w.position.x,
            top: w.position.y,
            width: w.size.width,
            height: w.size.height,
            zIndex: w.zIndex,
          }}
        >
          <OSWindow windowId={w.id} />
        </div>
      ))}
    </div>
  );
}