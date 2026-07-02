import { useRouter } from "next/navigation";
import { aiBrain } from "./ai/aiBrain";
import { useOSStore } from "@/store/useOSStore";

export function useOSCommand() {
  const router = useRouter();

  const { setActiveRoute, pushCommand } = useOSStore();

  const execute = async (input: string) => {
    const decision = await aiBrain(input);

    pushCommand({
      input,
      timestamp: Date.now(),
      type:
        decision.intent === "navigation" || decision.intent === "action"
          ? decision.intent
          : "unknown",
    });

    // NAVIGATION
    if (decision.intent === "navigation" && decision.target) {
      router.push(decision.target);
      setActiveRoute(decision.target);
      return decision;
    }

    // ACTION
    if (decision.intent === "action") {
      return {
        ...decision,
        executed: true,
      };
    }

    // QUERY (offline response)
    if (decision.intent === "query") {
      return decision;
    }

    return decision;
  };

  return { execute };
}
