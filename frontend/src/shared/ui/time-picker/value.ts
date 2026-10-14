import dayjs from 'dayjs';

/** Wall-clock time only: never convert the user's notification time to UTC. */
export function parseTime(value: string) {
  if (!/^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$/.test(value)) return null;
  return dayjs(`2000-01-01T${value.slice(0, 5)}:00`);
}
