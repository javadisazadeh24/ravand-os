"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Bot,
  CheckCircle2,
  CircleDashed,
  Clock3,
  Play,
  Send,
  Sparkles,
  TerminalSquare,
} from "lucide-react";
import { motion } from "framer-motion";

import GlassPanel from "@/components/os/GlassPanel";
import OSWindow from "@/components/os/OSWindow";
import { aiBrain } from "@/lib/ai/aiBrain";
import { eventBus } from "@/lib/core/eventBus";

type AgentLog = {
  type: string;
  payload: unknown;
  time: number;
};

const eventMeta: Record<
  string,
  { label: string; tone: string; icon: typeof Activity }
> = {
  "brain:decision": {
    label: "Brain decision",
    tone: "border-indigo-300/20 bg-indigo-400/10 text-indigo-100",
    icon: Sparkles,
  },
  "planner:created": {
    label: "Plan created",
    tone: "border-cyan-300/20 bg-cyan-400/10 text-cyan-100",
    icon: CircleDashed,
  },
  "agent:step": {
    label: "Agent step",
    tone: "border-amber-300/20 bg-amber-400/10 text-amber-100",
    icon: Play,
  },
  "agent:done": {
    label: "Execution complete",
    tone: "border-emerald-300/20 bg-emerald-400/10 text-emerald-100",
    icon: CheckCircle2,
  },
  "memory:write": {
    label: "Memory write",
    tone: "border-fuchsia-300/20 bg-fuchsia-400/10 text-fuchsia-100",
    icon: TerminalSquare,
  },
};

function formatPayload(payload: unknown) {
  if (payload === null || payload === undefined) return "No payload";
  if (typeof payload === "string") return payload;
  if (typeof payload === "number" || typeof payload === "boolean") {
    return String(payload);
  }

  if (typeof payload === "object") {
    const record = payload as Record<string, unknown>;
    const preferred =
      record.action ??
      record.status ??
      record.intent ??
      record.target ??
      record.response ??
      record.originalInput;

    if (typeof preferred === "string") return preferred;

    return Object.entries(record)
      .slice(0, 3)
      .map(([key, value]) => `${key}: ${String(value)}`)
      .join(" | ");
  }

  return "Event received";
}

export default function AgentsPage() {
  const [input, setInput] = useState("");
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [loading, setLoading] = useState(false);
  const latestLog = logs[0];

  useEffect(() => {
    const addLog = (type: string, payload: unknown) => {
      setLogs((prev) => [
        {
          type,
          payload,
          time: Date.now(),
        },
        ...prev,
      ]);
    };

    eventBus.on("brain:decision", (payload) => addLog("brain:decision", payload));
    eventBus.on("planner:created", (payload) => addLog("planner:created", payload));
    eventBus.on("agent:step", (payload) => addLog("agent:step", payload));
    eventBus.on("agent:done", (payload) => addLog("agent:done", payload));
    eventBus.on("memory:write", (payload) => addLog("memory:write", payload));

    return () => {
      eventBus.clear();
    };
  }, []);

  const runTask = async () => {
    if (!input.trim() || loading) return;

    setLoading(true);

    try {
      const decision = await aiBrain(input);
      setLogs((prev) => [
        {
          type: "brain:decision",
          payload: decision,
          time: Date.now(),
        },
        ...prev,
      ]);
    } finally {
      setLoading(false);
      setInput("");
    }
  };

  const progress = useMemo(() => {
    if (logs.length === 0) return 0;
    if (logs.some((log) => log.type === "agent:done")) return 100;
    return Math.min(88, 18 + logs.length * 14);
  }, [logs]);

  return (
    <div className="grid gap-5 xl:grid-cols-[0.9fr_1.2fr]">
      <OSWindow title="Agent Center" eyebrow="Autonomous execution">
        <div className="space-y-5">
          <div>
            <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.16em] text-white/45">
              <Bot size={14} className="text-indigo-300" />
              Current task
            </div>
            <h1 className="mt-2 text-2xl font-semibold text-white">
              Delegate work to the OS
            </h1>
            <p className="mt-2 text-sm text-white/55">
              The agent center turns commands into plans, execution steps, and
              memory events.
            </p>
          </div>

          <div className="rounded-[24px] border border-white/10 bg-white/[0.055] p-3">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder='Try "optimize system" or "run agent task"'
              className="min-h-28 w-full resize-none bg-transparent p-2 text-sm text-white outline-none placeholder:text-white/35"
              onKeyDown={(event) => {
                if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
                  void runTask();
                }
              }}
            />
            <div className="flex items-center justify-between gap-3 border-t border-white/10 pt-3">
              <span className="text-xs text-white/40">Cmd/Ctrl + Enter</span>
              <button
                type="button"
                onClick={() => void runTask()}
                className="flex items-center gap-2 rounded-2xl bg-indigo-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={loading}
              >
                {loading ? <Activity size={16} /> : <Send size={16} />}
                {loading ? "Running" : "Run agent"}
              </button>
            </div>
          </div>

          <GlassPanel className="p-4" intense>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-white/40">
                  Execution progress
                </p>
                <p className="mt-1 text-sm text-white/70">
                  {latestLog ? formatPayload(latestLog.payload) : "Awaiting task"}
                </p>
              </div>
              <span className="rounded-full border border-emerald-300/20 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-100">
                {loading ? "Active" : "Standby"}
              </span>
            </div>
            <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-indigo-400 via-cyan-300 to-emerald-300"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.45, ease: "easeOut" }}
              />
            </div>
          </GlassPanel>
        </div>
      </OSWindow>

      <OSWindow title="Execution Timeline" eyebrow="Live agent telemetry">
        <div className="space-y-4">
          {logs.length === 0 ? (
            <div className="grid min-h-[420px] place-items-center rounded-[28px] border border-dashed border-white/10 bg-white/[0.025] text-center">
              <div>
                <Clock3 className="mx-auto text-white/35" size={32} />
                <p className="mt-3 text-sm font-medium text-white/70">
                  Timeline is ready
                </p>
                <p className="mt-1 text-xs text-white/40">
                  Agent events will appear here as structured execution history.
                </p>
              </div>
            </div>
          ) : (
            logs.map((log, index) => {
              const meta = eventMeta[log.type] ?? {
                label: log.type,
                tone: "border-white/10 bg-white/[0.06] text-white/75",
                icon: Activity,
              };
              const Icon = meta.icon;

              return (
                <motion.div
                  key={`${log.type}-${log.time}-${index}`}
                  className="relative pl-10"
                  initial={{ opacity: 0, x: 18 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.24, ease: "easeOut" }}
                >
                  <div className="absolute left-4 top-10 h-full w-px bg-white/10" />
                  <div className="absolute left-0 top-1 grid size-8 place-items-center rounded-2xl border border-white/10 bg-[#151515] text-white/65">
                    <Icon size={15} />
                  </div>
                  <div className="rounded-[22px] border border-white/10 bg-white/[0.05] p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span
                        className={`rounded-full border px-3 py-1 text-xs ${meta.tone}`}
                      >
                        {meta.label}
                      </span>
                      <span className="text-xs text-white/35">
                        {new Date(log.time).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-white/72">
                      {formatPayload(log.payload)}
                    </p>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </OSWindow>
    </div>
  );
}
