"use client";

import { useState } from "react";
import { aiBrain } from "@/lib/ai/aiBrain";

type AgentTask = {
  input: string;
  status: "idle" | "running" | "done";
  result?: string;
};

export default function AgentsPage() {
  const [task, setTask] = useState("");
  const [tasks, setTasks] = useState<AgentTask[]>([]);

  const runAgent = async () => {
    if (!task.trim()) return;

    const newTask: AgentTask = {
      input: task,
      status: "running",
    };

    setTasks((prev) => [...prev, newTask]);
    setTask("");

    try {
      const result = await aiBrain(task);

      setTasks((prev) =>
        prev.map((t, i) =>
          i === prev.length - 1
            ? {
                ...t,
                status: "done",
                result:
                  result?.response ||
                  JSON.stringify(result, null, 2),
              }
            : t
        )
      );
    } catch (err) {
      setTasks((prev) =>
        prev.map((t, i) =>
          i === prev.length - 1
            ? {
                ...t,
                status: "done",
                result: "❌ Agent execution failed",
              }
            : t
        )
      );
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      runAgent();
    }
  };

  return (
    <div className="p-6 text-white min-h-screen bg-black">
      <h1 className="text-xl font-bold mb-4">
        RAVAND OS — Agent Control Center
      </h1>

      {/* Input */}
      <div className="flex gap-2 mb-6">
        <input
          value={task}
          onChange={(e) => setTask(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter agent task..."
          className="flex-1 px-3 py-2 rounded bg-white/5 outline-none border border-white/10"
        />

        <button
          onClick={runAgent}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded"
        >
          Run
        </button>
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {tasks.map((t, i) => (
          <div
            key={i}
            className="p-3 rounded bg-white/5 border border-white/10"
          >
            <div className="text-sm">
              <b>Task:</b> {t.input}
            </div>

            <div className="text-xs mt-1 opacity-70">
              Status: {t.status}
            </div>

            {t.result && (
              <div className="text-green-400 text-sm mt-2 whitespace-pre-wrap">
                {t.result}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}