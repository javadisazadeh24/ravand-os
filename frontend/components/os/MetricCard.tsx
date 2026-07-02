"use client";

import type { LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

import GlassPanel from "./GlassPanel";
import MiniChart from "./MiniChart";

type MetricCardProps = {
  title: string;
  value: string;
  detail: string;
  icon: LucideIcon;
  chart: number[];
  tone?: "indigo" | "emerald" | "amber" | "rose";
};

export default function MetricCard({
  title,
  value,
  detail,
  icon: Icon,
  chart,
  tone = "indigo",
}: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
    >
      <GlassPanel className="overflow-hidden p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.14em] text-white/45">
              {title}
            </p>
            <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
          </div>
          <div className="grid size-10 place-items-center rounded-2xl border border-white/10 bg-white/10 text-white">
            <Icon size={18} />
          </div>
        </div>

        <div className="mt-4">
          <MiniChart values={chart} tone={tone} />
        </div>

        <p className="mt-3 text-xs text-white/55">{detail}</p>
      </GlassPanel>
    </motion.div>
  );
}
