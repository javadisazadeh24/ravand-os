"use client";

import { Settings } from "lucide-react";

import SystemModulePage from "@/components/os/SystemModulePage";

export default function SettingsPage() {
  return (
    <SystemModulePage
      eyebrow="System controls"
      title="Settings"
      description="A focused OS preferences surface for workspace, interface, command, and safety controls."
      icon={Settings}
      signals={[
        { label: "Theme", value: "Dark glass" },
        { label: "Motion", value: "Smooth" },
        { label: "Shell", value: "Active" },
      ]}
      chart={[28, 30, 36, 34, 42, 49, 57, 62, 69]}
    />
  );
}
