import type { FastAction, FastIntent } from './worship.types';

export function prepareFastOperation(
  previous: FastAction | null,
  intent: FastIntent,
  newId: () => string
): FastAction {
  if (previous?.action === intent.action && previous.amount === intent.amount) return previous;
  return { ...intent, operationId: newId() };
}
