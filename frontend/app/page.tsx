"use client";

import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    const res = await fetch("http://127.0.0.1:8000/api/v1/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: input,
      }),
    });

    const data = await res.json();

    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: data.content },
    ]);

    setInput("");
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>RAVAND OS Chat</h1>

      <div style={{ marginTop: 20 }}>
        {messages.map((m, i) => (
          <div key={i}>
            <b>{m.role}:</b> {m.content}
          </div>
        ))}
      </div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type..."
        style={{ marginTop: 20, width: 300 }}
      />

      <button onClick={sendMessage} style={{ marginLeft: 10 }}>
        Send
      </button>
    </div>
  );
}