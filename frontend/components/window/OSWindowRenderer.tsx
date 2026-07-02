"use client";

import { useDesktopStore } from "@/store/useDesktopStore";
import { motion, AnimatePresence } from "framer-motion";

export default function OSWindowRenderer() {
  const windows = useDesktopStore((s) => s.windows);

  return (
    <div className="absolute inset-0 pointer-events-none">
      <AnimatePresence>
        {windows.map((window) => (
          <motion.div
            key={window.id}
            className="absolute pointer-events-auto"
            initial={{
              opacity: 0,
              scale: 0.94,
            }}
            animate={{
              opacity: 1,
              scale: 1,
            }}
            exit={{
              opacity: 0,
              scale: 0.94,
            }}
            transition={{
              duration: 0.18,
            }}
            style={{
              left: window.x,
              top: window.y,
              width: window.width,
              height: window.height,
              zIndex: window.zIndex,
            }}
          >
            <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#111111]/95 shadow-[0_25px_90px_rgba(0,0,0,.45)] backdrop-blur-xl">
              {/* Titlebar */}
              <div className="flex h-11 items-center justify-between border-b border-white/10 bg-white/[0.03] px-4">
                <span className="text-sm font-medium text-white">
                  {window.title}
                </span>

                <div className="flex gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500" />
                  <div className="h-3 w-3 rounded-full bg-yellow-500" />
                  <div className="h-3 w-3 rounded-full bg-green-500" />
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-auto p-5 text-sm text-white/70">
                <div className="font-medium">
                  {window.appId}
                </div>

                <div className="mt-3 text-white/40">
                  Window Renderer Connected
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}