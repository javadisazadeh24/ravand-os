"use client";

import { useEffect } from "react";
import { registerDefaultApps } from "@/lib/apps/registerDefaultApps";

export default function AppBootstrap() {
  useEffect(() => {
    registerDefaultApps();
  }, []);

  return null;
}