export function safeReturnPath(value: string | null, origin = 'https://deenly.uz'): string {
  if (!value || !value.startsWith('/') || value.startsWith('//') || value.includes('\\'))
    return '/';
  if ([...value].some((character) => character.charCodeAt(0) < 32)) return '/';
  try {
    const base = new URL(origin);
    const target = new URL(value, base);
    if (target.origin !== base.origin) return '/';
    return target.pathname + target.search + target.hash;
  } catch {
    return '/';
  }
}
