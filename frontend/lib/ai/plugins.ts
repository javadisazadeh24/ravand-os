export type Plugin = {
  name: string;
  match: (input: string) => boolean;
  run: (input: string) => string;
};

export const plugins: Plugin[] = [
  {
    name: "time",
    match: (input) => input.includes("time"),
    run: () => `Current system time: ${new Date().toLocaleTimeString()}`,
  },

  {
    name: "hello",
    match: (input) => input.includes("hello"),
    run: () => `Hello from RAVAND OS 👋`,
  },
];

export function runPlugins(input: string): string | null {
  for (const plugin of plugins) {
    if (plugin.match(input)) {
      return plugin.run(input);
    }
  }
  return null;
}