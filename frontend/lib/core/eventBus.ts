type EventHandler<T = any> = (payload: T) => void;

type EventMap = {
  "brain:decision": any;
  "planner:created": any;
  "agent:step": any;
  "agent:done": any;
  "memory:write": any;
  "tool:executed": any;
};

class EventBus {
  private listeners: {
    [K in keyof EventMap]?: EventHandler<EventMap[K]>[];
  } = {};

  /**
   * Subscribe to event
   */
  on<K extends keyof EventMap>(
    event: K,
    handler: EventHandler<EventMap[K]>
  ) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }

    this.listeners[event]!.push(handler);
  }

  /**
   * Emit event
   */
  emit<K extends keyof EventMap>(
    event: K,
    payload: EventMap[K]
  ) {
    const handlers = this.listeners[event];

    if (!handlers) return;

    for (const handler of handlers) {
      try {
        handler(payload);
      } catch (err) {
        console.error(`[EventBus Error] ${event}`, err);
      }
    }
  }

  /**
   * Clear all listeners (useful for dev hot reload)
   */
  clear() {
    this.listeners = {};
  }
}

export const eventBus = new EventBus();