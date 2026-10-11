/** A single playback lease across readers and exercises, without persisted user data. */
let current: { owner: object; pause: () => void } | null = null;
export const acquirePlayback = (owner: object, pause: () => void) => {
  if (current && current.owner !== owner) current.pause();
  current = { owner, pause };
};
export const releasePlayback = (owner: object) => {
  if (current?.owner === owner) current = null;
};
export const repeatFinished = (completed: number, repeat: number) => completed + 1 >= repeat;
export const audioTime = (seconds: number) => {
  const time = Math.max(0, Math.floor(Number.isFinite(seconds) ? seconds : 0));
  return `${Math.floor(time / 60)}:${String(time % 60).padStart(2, '0')}`;
};
