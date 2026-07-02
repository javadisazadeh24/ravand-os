import { parseCommand } from "./commandEngine";
import { useRouter } from "next/navigation";

export function useOSRouter() {
  const router = useRouter();

  const runCommand = (input: string) => {
    const command = parseCommand(input);

    if (command.type === "navigation" && command.target) {
      router.push(command.target);
      return;
    }

    return command;
  };

  return { runCommand };
}