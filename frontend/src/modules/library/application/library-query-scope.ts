import type { LibraryParams } from '../domain';

export function sameLibraryScope(
  previousLanguage: unknown,
  previousParams: LibraryParams | undefined,
  language: string,
  params: LibraryParams
): boolean {
  return (
    previousLanguage === language &&
    previousParams?.kind === params.kind &&
    previousParams.q === params.q
  );
}
