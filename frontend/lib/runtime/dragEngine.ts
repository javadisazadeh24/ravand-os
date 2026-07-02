class DragEngine {
  private start = { x: 0, y: 0 };
  private initial = { x: 0, y: 0 };
  private callback: ((pos: { x: number; y: number }) => void) | null = null;

  startDrag(
    _id: string,
    e: React.MouseEvent,
    initialPos: { x: number; y: number },
    cb: (pos: { x: number; y: number }) => void
  ) {
    this.start = { x: e.clientX, y: e.clientY };
    this.initial = initialPos;
    this.callback = cb;

    document.addEventListener("mousemove", this.move);
    document.addEventListener("mouseup", this.up);
  }

  move = (e: MouseEvent) => {
    if (!this.callback) return;

    this.callback({
      x: this.initial.x + (e.clientX - this.start.x),
      y: this.initial.y + (e.clientY - this.start.y),
    });
  };

  up = () => {
    this.callback = null;
    document.removeEventListener("mousemove", this.move);
    document.removeEventListener("mouseup", this.up);
  };
}

export const dragEngine = new DragEngine();