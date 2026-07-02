import { useRouter } from "next/navigation";
import { parseCommand } from "./commandEngine";

export function useOSCommand() {
  const router = useRouter();

  const execute = (input: string) => {
    const command = parseCommand(input);

    // NAVIGATION
    if (command.type === "navigation" && command.target) {
      router.push(command.target);
      return command;
    }

    // ACTION
    if (command.type === "action") {
      return {
        ...command,
        executed: true,
      };
    }

    return command;
  };

  return { execute };
}