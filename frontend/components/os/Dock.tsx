"use client";

import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";

import { sidebarItems } from "@/components/sidebar/sidebar.data";
import { cn } from "@/lib/utils";

export default function Dock() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <motion.nav
      aria-label="Application dock"
      className="fixed bottom-4 left-1/2 z-40 hidden -translate-x-1/2 items-end gap-2 rounded-[24px] border border-white/12 bg-black/35 px-3 py-2 shadow-[0_24px_70px_rgba(0,0,0,0.42),inset_0_1px_0_rgba(255,255,255,0.08)] backdrop-blur-2xl md:flex"
      initial={{ y: 26, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.36, ease: "easeOut", delay: 0.12 }}
    >
      {sidebarItems.map((item) => {
        const Icon = item.icon;
        const isActive =
          item.href === "/" ? pathname === item.href : pathname.startsWith(item.href);

        return (
          <motion.button
            key={item.href}
            type="button"
            title={item.title}
            aria-label={item.title}
            className={cn(
              "relative grid size-12 place-items-center rounded-[18px] border border-white/10 bg-white/[0.06] text-white/70 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)] transition hover:text-white",
              isActive && "bg-white/[0.13] text-white",
            )}
            whileHover={{ y: -8, scale: 1.12 }}
            whileTap={{ scale: 0.96 }}
            onClick={() => router.push(item.href)}
          >
            <Icon size={20} />
            {isActive ? (
              <motion.span
                layoutId="dock-active"
                className="absolute -bottom-1.5 size-1.5 rounded-full bg-white"
              />
            ) : null}
          </motion.button>
        );
      })}
    </motion.nav>
  );
}
