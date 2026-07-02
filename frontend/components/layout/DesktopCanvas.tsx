"use client";

import { ReactNode } from "react";

import WindowManager from "@/components/window/WindowManager";

type DesktopCanvasProps = {
  children: ReactNode;
};

export default function DesktopCanvas({
  children,
}: DesktopCanvasProps) {
  return (
    <div className="relative flex-1 overflow-hidden">
      {/* Pages */}
      <div className="relative z-0 h-full">
        {children}
      </div>

      {/* Floating Windows */}
      <WindowManager />
    </div>
  );
}