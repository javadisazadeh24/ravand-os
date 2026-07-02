"use client";

import { motion } from "framer-motion";

type MiniChartProps = {
  values: number[];
  tone?: "indigo" | "emerald" | "amber" | "rose";
};

const tones = {
  indigo: "from-indigo-400 to-violet-400",
  emerald: "from-emerald-300 to-cyan-300",
  amber: "from-amber-300 to-orange-400",
  rose: "from-rose-300 to-fuchsia-400",
};

export default function MiniChart({ values, tone = "indigo" }: MiniChartProps) {
  const maxValue = Math.max(...values, 1);

  return (
    <div className="flex h-20 items-end gap-1.5">
      {values.map((value, index) => (
        <motion.div
          key={`${value}-${index}`}
          className={`w-full rounded-t-full bg-gradient-to-t ${tones[tone]} opacity-80`}
          initial={{ height: 6, opacity: 0.25 }}
          animate={{
            height: `${Math.max(14, (value / maxValue) * 100)}%`,
            opacity: 0.8,
          }}
          transition={{ delay: index * 0.035, duration: 0.36, ease: "easeOut" }}
        />
      ))}
    </div>
  );
}
