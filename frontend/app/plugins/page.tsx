"use client";

import { Puzzle } from "lucide-react";

import SystemModulePage from "@/components/os/SystemModulePage";

export default function PluginsPage() {
  return (
    <SystemModulePage
      eyebrow="Extension layer"
      title="Plugins"
      description="A polished control surface for installed OS capabilities, tool extensions, and future connector management."
      icon={Puzzle}
      signals={[
        { label: "Registry", value: "Ready" },
        { label: "Connectors", value: "Modular" },
        { label: "Policy", value: "Scoped" },
      ]}
      chart={[18, 22, 31, 44, 39, 52, 61, 58, 67]}
    />
  );
}
