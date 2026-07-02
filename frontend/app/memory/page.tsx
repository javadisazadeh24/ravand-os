"use client";

import { Brain } from "lucide-react";

import SystemModulePage from "@/components/os/SystemModulePage";

export default function MemoryPage() {
  return (
    <SystemModulePage
      eyebrow="Memory fabric"
      title="Memory"
      description="A system-level view for notes, command memory, navigation records, and retrieval signals surfaced by the OS."
      icon={Brain}
      signals={[
        { label: "Recall", value: "Enabled" },
        { label: "Index", value: "Live" },
        { label: "Scope", value: "Local" },
      ]}
      chart={[12, 19, 24, 33, 48, 52, 63, 70, 76]}
    />
  );
}
