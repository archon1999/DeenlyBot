import type { AudioTrack } from 'src/shared/domain/audio';

export type AudioTrackDto = {
  id: string | number;
  label: string;
  voice: string;
  url: string;
  duration_ms?: number | null;
  segments?: { key: string; label: string; start_ms: number; end_ms: number }[];
  attribution?: string;
  source_url?: string;
};
export const mapAudioTracks = (tracks?: AudioTrackDto[]): AudioTrack[] =>
  (tracks ?? [])
    .filter(
      (track) =>
        /^https?:\/\//.test(track.url) ||
        (track.url.startsWith('/') && !track.url.startsWith('//') && !track.url.includes('\\'))
    )
    .map((track) => ({
      id: String(track.id),
      label: track.label,
      voice: track.voice,
      url: track.url,
      durationMs: track.duration_ms ?? null,
      segments: (track.segments ?? []).map((segment) => ({
        key: segment.key,
        label: segment.label,
        startMs: segment.start_ms,
        endMs: segment.end_ms,
      })),
      attribution: track.attribution ?? '',
      sourceUrl: /^https?:\/\//.test(track.source_url ?? '') ? track.source_url! : '',
    }));
