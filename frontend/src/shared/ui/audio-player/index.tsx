import type { AudioTrack } from 'src/shared/domain/audio';

import { useId, useRef, useState, useEffect } from 'react';

import {
  Box,
  Link,
  Alert,
  Stack,
  Button,
  Slider,
  SvgIcon,
  MenuItem,
  TextField,
  Typography,
  IconButton,
  CircularProgress,
} from '@mui/material';

import {
  audioTime,
  repeatFinished,
  acquirePlayback,
  releasePlayback,
} from 'src/shared/audio/playback';

import { useAudioLabels } from './labels';

function MediaIcon({ type }: { type: 'play' | 'pause' | 'previous' | 'next' }) {
  return (
    <SvgIcon viewBox="0 0 24 24">
      <g
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {type === 'play' && <path d="m8 4 12 8-12 8Z" />}
        {type === 'pause' && <path d="M8 4v16M16 4v16" />}
        {type === 'previous' && <path d="M5 4v16m14-16L7 12l12 8Z" />}
        {type === 'next' && <path d="M19 4v16M5 4l12 8-12 8Z" />}
      </g>
    </SvgIcon>
  );
}

/** Deliberate playback only. Closing a reader releases audio; playback never marks study progress. */
export function AudioPlayer({
  tracks,
  unavailable = false,
}: {
  tracks: AudioTrack[];
  unavailable?: boolean;
}) {
  const labels = useAudioLabels();
  const regionId = useId();
  const audio = useRef<HTMLAudioElement>(null);
  const cleanupMedia = useRef<HTMLAudioElement | null>(null);
  const lease = useRef({});
  const completed = useRef(0);
  const wantsPlayback = useRef(false);
  const request = useRef(0);
  const [index, setIndex] = useState(0);
  const [segmentKey, setSegmentKey] = useState('');
  const [repeat, setRepeat] = useState(1);
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [position, setPosition] = useState(0);
  const [duration, setDuration] = useState(0);
  const track = tracks[index] ?? tracks[0];
  const segment = track?.segments.find((value) => value.key === segmentKey);
  const startAt = (segment?.startMs ?? 0) / 1000;
  const endAt = segment ? segment.endMs / 1000 : duration || (track?.durationMs ?? 0) / 1000;
  const trackSignature = tracks.map((value) => `${value.id}:${value.url}`).join('|');
  useEffect(() => {
    setIndex(0);
    setSegmentKey('');
    setError(false);
    setPosition(0);
    setDuration(0);
    wantsPlayback.current = false;
    audio.current?.pause();
    releasePlayback(lease.current);
    setPlaying(false);
    setLoading(false);
  }, [trackSignature]);
  useEffect(() => {
    const owner = lease.current;
    return () => {
      wantsPlayback.current = false;
      request.current += 1;
      cleanupMedia.current?.pause();
      releasePlayback(owner);
    };
  }, []);
  const play = async () => {
    const media = audio.current;
    if (!media) return;
    cleanupMedia.current = media;
    const version = ++request.current;
    wantsPlayback.current = true;
    setError(false);
    setLoading(true);
    acquirePlayback(lease.current, () => {
      wantsPlayback.current = false;
      request.current += 1;
      media.pause();
      setLoading(false);
    });
    try {
      if (media.currentTime < startAt || (endAt && media.currentTime >= endAt - 0.05))
        media.currentTime = startAt;
      await media.play();
      if (version !== request.current || !wantsPlayback.current) {
        media.pause();
        return;
      }
      setLoading(false);
    } catch {
      if (version !== request.current || !wantsPlayback.current) return;
      setError(true);
      setLoading(false);
      setPlaying(false);
      wantsPlayback.current = false;
      releasePlayback(lease.current);
    }
  };
  const finish = () => {
    const media = audio.current;
    if (!media) return;
    if (!repeatFinished(completed.current, repeat)) {
      completed.current += 1;
      media.currentTime = startAt;
      void play();
    } else {
      wantsPlayback.current = false;
      media.pause();
      setPlaying(false);
      completed.current = 0;
      media.currentTime = startAt;
      setPosition(startAt);
      releasePlayback(lease.current);
    }
  };
  const selectTrack = (next: number) => {
    audio.current?.pause();
    releasePlayback(lease.current);
    completed.current = 0;
    wantsPlayback.current = false;
    request.current += 1;
    setPlaying(false);
    setLoading(false);
    setError(false);
    setPosition(0);
    setDuration(0);
    setSegmentKey('');
    setIndex(next);
  };
  if (!track)
    return unavailable ? (
      <Typography variant="body2" color="text.secondary">
        {labels.unavailable}
      </Typography>
    ) : null;
  return (
    <Box
      component="section"
      aria-labelledby={regionId}
      aria-busy={loading}
      sx={{ p: 2.5, borderRadius: 2, bgcolor: 'background.neutral' }}
    >
      <Stack spacing={2}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
          <Box sx={{ minWidth: 0 }}>
            <Typography id={regionId} variant="subtitle2">
              {labels.listen}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ overflowWrap: 'anywhere' }}>
              {track.label}
              {track.voice ? ` · ${track.voice}` : ''}
            </Typography>
          </Box>
          <IconButton
            color="primary"
            aria-label={playing || loading ? labels.pause : labels.play}
            onClick={() => {
              if (playing || loading) {
                wantsPlayback.current = false;
                request.current += 1;
                audio.current?.pause();
                setLoading(false);
                releasePlayback(lease.current);
              } else {
                completed.current = 0;
                void play();
              }
            }}
            sx={{ bgcolor: 'action.selected', width: 44, height: 44 }}
          >
            {loading ? (
              <CircularProgress size={22} aria-label={labels.loading} />
            ) : (
              <MediaIcon type={playing ? 'pause' : 'play'} />
            )}
          </IconButton>
        </Stack>
        <audio
          ref={audio}
          src={track.url}
          preload="none"
          onPlay={() => {
            if (!wantsPlayback.current) audio.current?.pause();
            else setPlaying(true);
          }}
          onPause={() => setPlaying(false)}
          onWaiting={() => {
            if (wantsPlayback.current) setLoading(true);
          }}
          onPlaying={() => setLoading(false)}
          onLoadedMetadata={() => {
            const length = audio.current?.duration ?? 0;
            setDuration(Number.isFinite(length) ? length : 0);
          }}
          onTimeUpdate={() => {
            const media = audio.current;
            if (!media) return;
            setPosition(media.currentTime);
            if (segment && playing && media.currentTime >= endAt) finish();
          }}
          onEnded={finish}
          onError={() => {
            setError(true);
            setLoading(false);
            setPlaying(false);
            wantsPlayback.current = false;
            releasePlayback(lease.current);
          }}
        />
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <Typography variant="caption" sx={{ minWidth: 30 }}>
            {audioTime(position - startAt)}
          </Typography>
          <Slider
            aria-label={labels.seek}
            size="small"
            value={Math.max(startAt, Math.min(position, endAt || startAt))}
            min={startAt}
            max={endAt > startAt ? endAt : startAt + 1}
            disabled={!duration}
            onChange={(_, value) => {
              if (audio.current) {
                audio.current.currentTime = value as number;
                setPosition(value as number);
              }
            }}
          />
          <Typography variant="caption" sx={{ minWidth: 30 }}>
            {audioTime(endAt - startAt)}
          </Typography>
        </Stack>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          {tracks.length > 1 && (
            <TextField
              select
              size="small"
              label={labels.track}
              value={index}
              onChange={(event) => selectTrack(Number(event.target.value))}
              sx={{ flex: 1 }}
            >
              {tracks.map((value, trackIndex) => (
                <MenuItem key={value.id} value={trackIndex}>
                  {value.label}
                </MenuItem>
              ))}
            </TextField>
          )}
          {!!track.segments.length && (
            <TextField
              select
              size="small"
              label={labels.segment}
              value={segmentKey}
              onChange={(event) => {
                wantsPlayback.current = false;
                request.current += 1;
                audio.current?.pause();
                releasePlayback(lease.current);
                setLoading(false);
                setSegmentKey(event.target.value);
                completed.current = 0;
              }}
              sx={{ flex: 1 }}
            >
              <MenuItem value="">{labels.full}</MenuItem>
              {track.segments.map((value) => (
                <MenuItem key={value.key} value={value.key}>
                  {value.label}
                </MenuItem>
              ))}
            </TextField>
          )}
          <TextField
            select
            size="small"
            label={labels.repeat}
            value={repeat}
            onChange={(event) => {
              setRepeat(Number(event.target.value));
              completed.current = 0;
            }}
            sx={{ minWidth: 110 }}
          >
            {[1, 3, 5].map((value) => (
              <MenuItem key={value} value={value}>
                {value}×
              </MenuItem>
            ))}
          </TextField>
          {tracks.length > 1 && (
            <Stack direction="row" alignItems="center">
              <IconButton
                aria-label={labels.previous}
                disabled={index === 0}
                onClick={() => selectTrack(index - 1)}
              >
                <MediaIcon type="previous" />
              </IconButton>
              <IconButton
                aria-label={labels.next}
                disabled={index >= tracks.length - 1}
                onClick={() => selectTrack(index + 1)}
              >
                <MediaIcon type="next" />
              </IconButton>
            </Stack>
          )}
        </Stack>
        {error && (
          <Alert
            severity="warning"
            action={
              <Button
                color="inherit"
                size="small"
                onClick={() => {
                  audio.current?.load();
                  void play();
                }}
              >
                {labels.retry}
              </Button>
            }
          >
            {labels.error}
          </Alert>
        )}
        {track.attribution && (
          <Typography variant="caption" color="text.secondary">
            {track.sourceUrl ? (
              <Link
                href={track.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                color="inherit"
                aria-label={`${labels.credit}: ${track.attribution}`}
              >
                {track.attribution}
              </Link>
            ) : (
              track.attribution
            )}
          </Typography>
        )}
      </Stack>
    </Box>
  );
}
