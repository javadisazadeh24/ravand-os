"use client";

import { useState } from "react";
import {
  Activity,
  Bot,
  Brain,
  Cpu,
  HardDrive,
  MessageSquare,
  Network,
  Send,
  Sparkles,
} from "lucide-react";
import { motion } from "framer-motion";

import GlassPanel from "@/components/os/GlassPanel";
import MetricCard from "@/components/os/MetricCard";
import MiniChart from "@/components/os/MiniChart";
import OSWindow from "@/components/os/OSWindow";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const metrics = [
  {
    title: "Neural Load",
    value: "42%",
    detail: "Adaptive routing capacity",
    icon: Cpu,
    chart: [28, 34, 31, 46, 40, 55, 42],
    tone: "indigo" as const,
  },
  {
    title: "Memory Index",
    value: "1.2k",
    detail: "Short and long term records",
    icon: Brain,
    chart: [18, 29, 38, 42, 58, 62, 71],
    tone: "emerald" as const,
  },
  {
    title: "Agent Runs",
    value: "18",
    detail: "Automations this session",
    icon: Bot,
    chart: [8, 12, 19, 16, 22, 30, 26],
    tone: "amber" as const,
  },
  {
    title: "System IO",
    value: "9.8ms",
    detail: "Interface response window",
    icon: Network,
    chart: [44, 38, 32, 26, 21, 18, 14],
    tone: "rose" as const,
  },
];

const agents = [
  { name: "Planner", status: "Ready", load: "Low" },
  { name: "Memory Curator", status: "Indexing", load: "Medium" },
  { name: "Tool Router", status: "Listening", load: "Low" },
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || isSending) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
        }),
      });

      const data = (await res.json()) as { content?: string };

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.content ?? "No response content." },
      ]);
    } finally {
      setIsSending(false);
      setInput("");
    }
  };

  return (
    <div className="space-y-5">
      <motion.div
        className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-white/45">
            <Sparkles size={14} className="text-indigo-300" />
            Desktop Environment
          </div>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            RAVAND OS
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-white/55">
            A command-first AI workspace for agents, memory, tools, and system
            orchestration.
          </p>
        </div>

        <GlassPanel className="flex items-center gap-3 px-4 py-3">
          <span className="grid size-9 place-items-center rounded-2xl bg-emerald-400/15 text-emerald-200">
            <Activity size={17} />
          </span>
          <div>
            <p className="text-xs text-white/45">System status</p>
            <p className="text-sm font-medium text-white">Interface nominal</p>
          </div>
        </GlassPanel>
      </motion.div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <MetricCard key={metric.title} {...metric} />
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <OSWindow title="Mission Control" eyebrow="Dashboard">
          <div className="grid gap-4 lg:grid-cols-2">
            <GlassPanel className="p-4" intense>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.16em] text-white/40">
                    Throughput
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-white">
                    86 operations
                  </p>
                </div>
                <HardDrive className="text-white/45" size={22} />
              </div>
              <div className="mt-5">
                <MiniChart
                  values={[34, 48, 42, 64, 58, 72, 69, 82, 76, 88]}
                  tone="emerald"
                />
              </div>
            </GlassPanel>

            <GlassPanel className="p-4" intense>
              <p className="text-xs uppercase tracking-[0.16em] text-white/40">
                Running agents
              </p>
              <div className="mt-4 space-y-3">
                {agents.map((agent) => (
                  <div
                    key={agent.name}
                    className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.045] px-3 py-2"
                  >
                    <div className="flex items-center gap-3">
                      <span className="grid size-8 place-items-center rounded-xl bg-indigo-400/15 text-indigo-200">
                        <Bot size={15} />
                      </span>
                      <div>
                        <p className="text-sm font-medium text-white">
                          {agent.name}
                        </p>
                        <p className="text-xs text-white/45">{agent.status}</p>
                      </div>
                    </div>
                    <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-xs text-white/55">
                      {agent.load}
                    </span>
                  </div>
                ))}
              </div>
            </GlassPanel>
          </div>
        </OSWindow>

        <OSWindow title="Chat Kernel" eyebrow="Live interface">
          <div className="flex min-h-[360px] flex-col">
            <div className="flex-1 space-y-3 overflow-y-auto pr-1">
              {messages.length === 0 ? (
                <div className="grid min-h-52 place-items-center rounded-3xl border border-dashed border-white/10 bg-white/[0.025] text-center">
                  <div>
                    <MessageSquare className="mx-auto text-white/35" size={28} />
                    <p className="mt-3 text-sm text-white/50">
                      Start a conversation with the local chat API.
                    </p>
                  </div>
                </div>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={`max-w-[85%] rounded-3xl px-4 py-3 text-sm ${
                      message.role === "user"
                        ? "ml-auto bg-indigo-500/25 text-white"
                        : "bg-white/[0.06] text-white/75"
                    }`}
                  >
                    {message.content}
                  </div>
                ))
              )}
            </div>

            <div className="mt-4 flex gap-2 rounded-2xl border border-white/10 bg-white/[0.05] p-2">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") void sendMessage();
                }}
                placeholder="Ask the OS..."
                className="min-w-0 flex-1 bg-transparent px-2 text-sm text-white outline-none placeholder:text-white/35"
              />
              <button
                type="button"
                onClick={() => void sendMessage()}
                className="grid size-10 place-items-center rounded-xl bg-indigo-500 text-white transition hover:bg-indigo-400"
              >
                <Send size={17} />
              </button>
            </div>
          </div>
        </OSWindow>
      </div>
    </div>
  );
}
