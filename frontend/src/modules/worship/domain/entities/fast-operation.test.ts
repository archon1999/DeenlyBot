import { it, vi, expect, describe } from 'vitest';

import { prepareFastOperation } from './fast-operation';

describe('fast command retry identity', () => {
  it('reuses an ambiguous operation until its result is confirmed', () => {
    const newId = vi.fn().mockReturnValueOnce('operation-1').mockReturnValueOnce('operation-2');
    const first = prepareFastOperation(null, { action: 'complete', amount: 1 }, newId);
    const retry = prepareFastOperation(first, { action: 'complete', amount: 1 }, newId);
    expect(retry.operationId).toBe('operation-1');
    expect(newId).toHaveBeenCalledTimes(1);
    const changedIntent = prepareFastOperation(retry, { action: 'add', amount: 1 }, newId);
    expect(changedIntent.operationId).toBe('operation-2');
  });
  it('creates a new identity for another confirmed completion', () => {
    const result = prepareFastOperation(
      null,
      { action: 'complete', amount: 1 },
      () => 'next-operation'
    );
    expect(result.operationId).toBe('next-operation');
  });
});
