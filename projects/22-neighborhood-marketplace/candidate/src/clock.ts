export type ClockFn = () => number;

/**
 * A clock that reads from a `base` function (real time by default) plus a
 * debug-controlled offset. Used to give the app one shared, adjustable
 * notion of "now" so that time-based behavior (like a reservation
 * expiring) can be explored deterministically — via `POST
 * /debug/advance-time` — without waiting in real time.
 */
export function createOffsetClock(base: ClockFn = () => Date.now()) {
  let offsetMs = 0;

  return {
    now(): number {
      return base() + offsetMs;
    },
    advance(byMs: number): void {
      offsetMs += byMs;
    },
    reset(): void {
      offsetMs = 0;
    },
  };
}

export type OffsetClock = ReturnType<typeof createOffsetClock>;
