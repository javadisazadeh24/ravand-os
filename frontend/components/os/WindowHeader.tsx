"use client";

import { Maximize2, Minus, X } from "lucide-react";

type Props = {
  windowId: string;
  title: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  isMaximized: boolean;

  onClose: () => void;
  onMinimize: () => void;
  onMaximize: () => void;

  onMove: (pos: { x: number; y: number }) => void;
  onResize: (size: { width: number; height: number }) => void;
};

export default function WindowHeader({
  title,
  isMaximized,
  onClose,
  onMinimize,
  onMaximize,
}: Props) {
  return (
    <div className="h-10 flex items-center justify-between px-3 bg-white/5 border-b border-white/10 cursor-move">
      {/* Title */}
      <span className="text-white/80 text-sm">{title}</span>

      {/* Controls */}
      <div className="flex gap-2">
        <button
          onClick={onMinimize}
          className="w-6 h-6 bg-yellow-500/60 rounded flex items-center justify-center"
        >
          <Minus size={12} />
        </button>

        <button
          onClick={onMaximize}
          className="w-6 h-6 bg-green-500/60 rounded flex items-center justify-center"
        >
          <Maximize2 size={12} />
        </button>

        <button
          onClick={onClose}
          className="w-6 h-6 bg-red-500/60 rounded flex items-center justify-center"
        >
          <X size={12} />
        </button>
      </div>
    </div>
  );
}