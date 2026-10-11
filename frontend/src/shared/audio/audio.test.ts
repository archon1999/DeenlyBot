import { it, vi, expect, describe } from 'vitest';

import { mapAudioTracks } from './audio.dto';
import { audioTime, repeatFinished, acquirePlayback, releasePlayback } from './playback';

describe('shared audio contract and playback lease', () => {
  it('maps timestamps, attribution and uploaded media without transport fields', () => {
    const track = mapAudioTracks([
      {
        id: 12,
        label: 'Ayah 1',
        voice: 'Reciter',
        url: '/media/audio/1.mp3',
        duration_ms: 3000,
        segments: [{ key: '1:1', label: '1:1', start_ms: 0, end_ms: 3000 }],
        attribution: 'Verified source',
        source_url: 'https://example.com/audio',
      },
    ])[0];
    expect(track).toMatchObject({
      id: '12',
      durationMs: 3000,
      url: '/media/audio/1.mp3',
      attribution: 'Verified source',
      segments: [{ key: '1:1', label: '1:1', startMs: 0, endMs: 3000 }],
    });
    expect(track).not.toHaveProperty('duration_ms');
    expect(track.segments[0]).not.toHaveProperty('start_ms');
  });
  it('rejects executable and protocol-relative source URLs', () => {
    expect(
      mapAudioTracks([{ id: 'x', label: 'X', voice: '', url: 'javascript:alert(1)' }])
    ).toEqual([]);
    expect(
      mapAudioTracks([{ id: 'x', label: 'X', voice: '', url: '//example.com/a.mp3' }])
    ).toEqual([]);
    expect(
      mapAudioTracks([
        {
          id: 'x',
          label: 'X',
          voice: '',
          url: 'https://example.com/a.mp3',
          source_url: 'javascript:alert(1)',
        },
      ])[0].sourceUrl
    ).toBe('');
  });
  it('acquiring a new player pauses the previous one but release cannot stop a newer player', () => {
    const first = {};
    const second = {};
    const third = {};
    const firstPause = vi.fn();
    const secondPause = vi.fn();
    acquirePlayback(first, firstPause);
    acquirePlayback(second, secondPause);
    expect(firstPause).toHaveBeenCalledTimes(1);
    releasePlayback(first);
    acquirePlayback(third, vi.fn());
    expect(secondPause).toHaveBeenCalledTimes(1);
    releasePlayback(third);
  });
  it.each([1, 3, 5])('ends only after exactly %i requested repetitions', (repeat) => {
    for (let completed = 0; completed < repeat; completed += 1)
      expect(repeatFinished(completed, repeat)).toBe(completed === repeat - 1);
  });
  it('formats finite positions without NaN or negative time', () => {
    expect(audioTime(65.9)).toBe('1:05');
    expect(audioTime(-10)).toBe('0:00');
    expect(audioTime(NaN)).toBe('0:00');
  });
});
