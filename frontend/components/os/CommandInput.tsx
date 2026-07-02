"use client";

import { useState } from "react";
import { useCommandRouter } from "@/hooks/useCommandRouter";

export default function CommandInput() {
  const [value, setValue] = useState("");
  const [status, setStatus] = useState("");

  const { execute } = useCommandRouter();

  async function run() {
    if (!value.trim()) return;

    const result = await execute(value);

    setStatus(result.response);
    setValue("");
  }

  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-[#111]/90 p-3 backdrop-blur-xl">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            void run();
          }
        }}
        placeholder="Command Ravand..."
        className="flex-1 bg-transparent text-white outline-none placeholder:text-white/35"
      />

      <button
        onClick={() => void run()}
        className="rounded-xl bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-500"
      >
        Enter
      </button>

      {status && (
        <span className="text-xs text-emerald-300 whitespace-nowrap">
          {status}
        </span>
      )}
    </div>
  );
}