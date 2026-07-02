import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type GlassPanelProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
  intense?: boolean;
};

export default function GlassPanel({
  children,
  className,
  intense = false,
  ...props
}: GlassPanelProps) {
  return (
    <div
      className={cn(
        "rounded-[22px] border border-white/10 shadow-[0_24px_80px_rgba(0,0,0,0.32),inset_0_1px_0_rgba(255,255,255,0.07)] backdrop-blur-2xl",
        intense ? "bg-white/[0.095]" : "bg-white/[0.055]",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
