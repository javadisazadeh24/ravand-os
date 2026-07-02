class ResizeEngine {
  private state: any = null;
  private cb: any = null;

  startResize(
    _id: string,
    dir: string,
    e: React.MouseEvent,
    size: any,
    pos: any,
    cb: any
  ) {
    this.state = {
      dir,
      startX: e.clientX,
      startY: e.clientY,
      size,
      pos,
    };

    this.cb = cb;

    document.addEventListener("mousemove", this.move);
    document.addEventListener("mouseup", this.up);
  }

  move = (e: MouseEvent) => {
    if (!this.state || !this.cb) return;

    let { width, height } = this.state.size;
    let { x, y } = this.state.pos;

    const dx = e.clientX - this.state.startX;
    const dy = e.clientY - this.state.startY;

    if (this.state.dir.includes("e")) width += dx;
    if (this.state.dir.includes("s")) height += dy;
    if (this.state.dir.includes("w")) {
      width -= dx;
      x += dx;
    }
    if (this.state.dir.includes("n")) {
      height -= dy;
      y += dy;
    }

    this.cb(
      {
        width: Math.max(400, width),
        height: Math.max(300, height),
      },
      { x, y }
    );
  };

  up = () => {
    this.state = null;
    this.cb = null;

    document.removeEventListener("mousemove", this.move);
    document.removeEventListener("mouseup", this.up);
  };
}

export const resizeEngine = new ResizeEngine();