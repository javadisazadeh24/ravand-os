"use client";

import type { LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

import GlassPanel from "./GlassPanel";
import MiniChart from "./MiniChart";
import OSWindow from "./OSWindow";

type ModuleSignal = {
  label: string;
  value: string;
};

type SystemModulePageProps = {
  eyebrow: string;
  title: string;
  description: string;
  icon: LucideIcon;
  signals: ModuleSignal[];
  chart: number[];
};

export default function SystemModulePage({
  eyebrow,
  title,
  description,
  icon: Icon,
  signals,
  chart,
}: SystemModulePageProps) {
  return (
    <OSWindow title={title} eyebrow={eyebrow}>
      <div className="space-y-5">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
          <div>
            <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.16em] text-white/45">
              <Icon size={14} className="text-indigo-300" />
              {eyebrow}
            </div>
            <h1 className="mt-2 text-3xl font-semibold text-white">{title}</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-white/55">
              {description}
            </p>
          </div>
          <div className="grid size-14 place-items-center rounded-[24px] border border-white/10 bg-white/[0.07] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
            <Icon size={24} />
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {signals.map((signal, index) => (
            <motion.div
              key={signal.label}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <GlassPanel className="p-4" intense>
                <p className="text-xs uppercase tracking-[0.16em] text-white/40">
                  {signal.label}
                </p>
                <p className="mt-2 text-xl font-semibold text-white">
                  {signal.value}
                </p>
              </GlassPanel>
            </motion.div>
          ))}
        </div>

        <GlassPanel className="p-5">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.16em] text-white/40">
                Activity shape
              </p>
              <p className="mt-1 text-sm text-white/55">
                Interface-level telemetry view
              </p>
            </div>
            <span className="rounded-full border border-emerald-300/20 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-100">
              Available
            </span>
          </div>
          <MiniChart values={chart} tone="indigo" />
        </GlassPanel>
      </div>
    </OSWindow>
  );
}
