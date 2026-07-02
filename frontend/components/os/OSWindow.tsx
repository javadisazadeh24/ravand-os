"use client";

import type { ReactNode } from "react";
import { useState } from "react";
import { Maximize2, Minus, X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

import { cn } from "@/lib/utils";

type OSWindowProps = {
  title: string;
  eyebrow?: string;
  children: ReactNode;
  className?: string;
  defaultPosition?: { x: number; y: number };
  defaultSize?: { width: number | string; minHeight?: number };
};

export default function OSWindow({
  title,
  eyebrow,
  children,
  className,
  defaultPosition = { x: 0, y: 0 },
  defaultSize = { width: "100%", minHeight: 260 },
}: OSWindowProps) {
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [isClosed, setIsClosed] = useState(false);

  if (isClosed) {
    return null;
  }

  return (
    <motion.section
      drag={!isMaximized}
      dragMomentum={false}
      initial={{ opacity: 0, scale: 0.97, x: defaultPosition.x, y: defaultPosition.y }}
      animate={{ opacity: 1, scale: 1, x: defaultPosition.x, y: defaultPosition.y }}
      whileDrag={{ scale: 1.01 }}
      transition={{ duration: 0.28, ease: "easeOut" }}
      style={{
        width: isMaximized ? "100%" : defaultSize.width,
        minHeight: isMinimized ? undefined : defaultSize.minHeight,
      }}
      className={cn(
        "group overflow-hidden rounded-[24px] border border-white/12 bg-[#111]/70 shadow-[0_28px_90px_rgba(0,0,0,0.38),inset_0_1px_0_rgba(255,255,255,0.08)] backdrop-blur-2xl",
        !isMaximized && !isMinimized && "resize overflow-auto",
        isMaximized && "min-h-[calc(100vh-12rem)]",
        className,
      )}
    >
      <div className="flex cursor-grab items-center justify-between gap-3 border-b border-white/10 bg-white/[0.045] px-4 py-3 active:cursor-grabbing">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              aria-label="Close window"
              className="grid size-3.5 place-items-center rounded-full bg-[#ff5f57] text-black/50 opacity-90 transition hover:opacity-100"
              onClick={() => setIsClosed(true)}
            >
              <X size={8} />
            </button>
            <button
              type="button"
              aria-label="Minimize window"
              className="grid size-3.5 place-items-center rounded-full bg-[#ffbd2e] text-black/50 opacity-90 transition hover:opacity-100"
              onClick={() => setIsMinimized((value) => !value)}
            >
              <Minus size={8} />
            </button>
            <button
              type="button"
              aria-label="Maximize window"
              className="grid size-3.5 place-items-center rounded-full bg-[#28c840] text-black/50 opacity-90 transition hover:opacity-100"
              onClick={() => {
                setIsMaximized((value) => !value);
                setIsMinimized(false);
              }}
            >
              <Maximize2 size={8} />
            </button>
          </div>

          <div className="min-w-0">
            {eyebrow ? (
              <p className="text-[10px] font-medium uppercase tracking-[0.16em] text-white/40">
                {eyebrow}
              </p>
            ) : null}
            <h2 className="truncate text-sm font-semibold text-white">{title}</h2>
          </div>
        </div>

        <div className="hidden h-1.5 w-16 rounded-full bg-white/10 sm:block" />
      </div>

      <AnimatePresence initial={false}>
        {!isMinimized ? (
          <motion.div
            className="p-4 sm:p-5"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.18 }}
          >
            {children}
          </motion.div>
        ) : null}
      </AnimatePresence>
    </motion.section>
  );
}
