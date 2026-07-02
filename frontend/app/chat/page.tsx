"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Bot, Command, Send, UserRound } from "lucide-react";
import { motion } from "framer-motion";

import OSWindow from "@/components/os/OSWindow";
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
    const currentInput = input;

    setMessages((prev) => [...prev, { role: "user", content: currentInput }]);
    setInput("");

    if (command.type === "navigation" && command.target) {
      setTimeout(() => {
        router.push(command.target!);
      }, 300);
      return;
    }

    if (command.type === "action") {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Executed: ${command.message}`,
          },
        ]);
      }, 400);
      return;
    }

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Unknown command: "${currentInput}"`,
        },
      ]);
    }, 400);
  };

  return (
    <OSWindow title="Chat Kernel" eyebrow="Command line interface">
      <div className="flex min-h-[620px] flex-col">
        <div className="mb-4 flex items-center gap-3 rounded-[24px] border border-white/10 bg-white/[0.05] p-4">
          <div className="grid size-11 place-items-center rounded-2xl bg-indigo-400/15 text-indigo-200">
            <Command size={20} />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white">Ask or command</h1>
            <p className="text-sm text-white/50">
              Navigate, execute local actions, or talk to the OS command parser.
            </p>
          </div>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto rounded-[24px] border border-white/10 bg-black/15 p-4">
          {messages.length === 0 ? (
            <div className="grid h-full min-h-72 place-items-center text-center">
              <div>
                <Bot className="mx-auto text-white/30" size={34} />
                <p className="mt-3 text-sm text-white/50">
                  Try /agents, /dashboard, or an action command.
                </p>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <motion.div
                key={`${message.role}-${index}`}
                className={`flex gap-3 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {message.role === "assistant" ? (
                  <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-white/10 text-white/65">
                    <Bot size={15} />
                  </span>
                ) : null}
                <div
                  className={`max-w-2xl rounded-3xl px-4 py-3 text-sm leading-6 ${
                    message.role === "user"
                      ? "bg-indigo-500/25 text-white"
                      : "bg-white/[0.06] text-white/75"
                  }`}
                >
                  {message.content}
                </div>
                {message.role === "user" ? (
                  <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-indigo-400/20 text-indigo-100">
                    <UserRound size={15} />
                  </span>
                ) : null}
              </motion.div>
            ))
          )}
        </div>

        <div className="mt-4 flex gap-2 rounded-[22px] border border-white/10 bg-white/[0.055] p-2">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") void sendMessage();
            }}
            className="min-w-0 flex-1 bg-transparent px-3 text-sm text-white outline-none placeholder:text-white/35"
            placeholder="Type a command..."
          />
          <button
            type="button"
            onClick={() => void sendMessage()}
            className="grid size-11 place-items-center rounded-2xl bg-indigo-500 text-white transition hover:bg-indigo-400"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </OSWindow>
  );
}
