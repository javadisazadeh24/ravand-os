"use client";

import { useEffect, useState } from "react";
import { aiBrain } from "@/lib/ai/aiBrain";
import { eventBus } from "@/lib/core/eventBus";

/**
 * 🧠 RAVAND OS — Agent Control Center UI
 */

type Log = {
  type: string;
  payload: any;
  time: number;
};

export default function AgentsPage() {
  const [input, setInput] = useState("");
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState(false);

  /**
   * EVENT LISTENERS
   */
  useEffect(() => {
    const addLog = (type: string, payload: any) => {
      setLogs((prev) => [
        {
          type,
          payload,
          time: Date.now(),
        },
        ...prev,
      ]);
    };

    eventBus.on("brain:decision", (p) => addLog("brain:decision", p));
    eventBus.on("planner:created", (p) => addLog("planner:created", p));
    eventBus.on("agent:step", (p) => addLog("agent:step", p));
    eventBus.on("agent:done", (p) => addLog("agent:done", p));
    eventBus.on("memory:write", (p) => addLog("memory:write", p));

    return () => {
      eventBus.clear();
    };
  }, []);

  /**
   * RUN TASK
   */
  const runTask = async () => {
    if (!input.trim()) return;

    setLoading(true);

    try {
      await aiBrain(input);
    } finally {
      setLoading(false);
      setInput("");
    }
  };

  return (
    <div className="h-screen flex bg-black text-white">
      
      {/* LEFT PANEL */}
      <div className="w-1/3 border-r border-white/10 p-4 flex flex-col gap-3">
        <h1 className="text-lg font-bold">
          🧠 RAVAND OS — Agent Control Center
        </h1>

        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter agent task..."
          className="bg-white/10 p-2 rounded outline-none"
          onKeyDown={(e) => e.key === "Enter" && runTask()}
        />

        <button
          onClick={runTask}
          className="bg-indigo-600 hover:bg-indigo-500 p-2 rounded"
        >
          {loading ? "Running..." : "Run"}
        </button>

        <div className="text-xs text-white/60 mt-4">
          Tip: try → "optimize system", "open dashboard", "run agent task"
        </div>
      </div>

      {/* RIGHT PANEL — LIVE LOGS */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3">
        {logs.map((log, i) => (
          <div
            key={i}
            className="bg-white/5 p-3 rounded border border-white/10"
          >
            <div className="text-xs text-white/50">
              {log.type}
            </div>

            <pre className="text-xs mt-2 overflow-x-auto">
              {JSON.stringify(log.payload, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}