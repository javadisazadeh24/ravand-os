"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { parseCommand } from "@/lib/commandEngine";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const router = useRouter();

  const sendMessage = async () => {
    if (!input.trim()) return;

    const command = parseCommand(input);

    // Add user message
    setMessages((prev) => [
      ...prev,
      { role: "user", content: input }
    ]);

    setInput("");

    // -------------------------
    // NAVIGATION COMMAND
    // -------------------------
    if (command.type === "navigation" && command.target) {
      setTimeout(() => {
        router.push(command.target!);
      }, 300);
      return;
    }

    // -------------------------
    // ACTION COMMAND
    // -------------------------
    if (command.type === "action") {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `⚙️ Executed: ${command.message}`
          }
        ]);
      }, 400);
      return;
    }

    // -------------------------
    // UNKNOWN COMMAND
    // -------------------------
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `❌ Unknown command: "${input}"`
        }
      ]);
    }, 400);
  };

  return (
    <div className="h-screen flex flex-col bg-[#0A0A0A] text-white">
      
      {/* Header */}
      <div className="h-12 border-b border-white/10 flex items-center px-4">
        <span className="text-sm font-medium">
          RAVAND OS — Chat Kernel
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`text-sm p-3 rounded-lg max-w-xl ${
              msg.role === "user"
                ? "bg-indigo-500/20 ml-auto"
                : "bg-white/5"
            }`}
          >
            {msg.content}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="border-t border-white/10 p-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          className="flex-1 bg-white/5 px-3 py-2 rounded-lg outline-none"
          placeholder="Type a command (/chat, /dashboard, /echo ...)"
        />

        <button
          onClick={sendMessage}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg"
        >
          Send
        </button>
      </div>
    </div>
  );
}