/** Framework-free media contract shared by learning modules. */
export type AudioSegment = { key: string; label: string; startMs: number; endMs: number };
export type AudioTrack = {
  id: string;
  label: string;
  voice: string;
  url: string;
  durationMs: number | null;
  segments: AudioSegment[];
  attribution: string;
  sourceUrl: string;
};
export type PracticeMode = 'text' | 'listening';
