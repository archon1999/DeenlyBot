import { useRef, useState, useEffect } from 'react';

export type FailureLanguage = 'uz' | 'ru' | 'en';
export const failureLabels = {
  uz: {
    notFound: 'Bu sahifa topilmadi',
    notFoundHint:
      'Bu manzil o‘zgargan yoki sahifa hali mavjud emas. Ilm va ibodat yo‘lingizni bosh sahifadan davom ettiring.',
    error: 'Sahifani ochib bo‘lmadi',
    errorHint:
      'Kutilmagan xatolik yuz berdi. Sahifani qayta yuklab ko‘ring yoki bosh sahifaga qayting.',
    home: 'Bosh sahifaga qaytish',
    retry: 'Qayta urinish',
    note: 'Har bir kichik qadam — yangi imkoniyat.',
    language: 'Tilni tanlash',
    light: 'Yorug‘ ko‘rinish',
    dark: 'Qorong‘i ko‘rinish',
    theme: 'Ko‘rinish',
  },
  ru: {
    notFound: 'Эта страница не найдена',
    notFoundHint:
      'Адрес изменился или страницы пока нет. Продолжите путь знаний и поклонения с главной страницы.',
    error: 'Не удалось открыть страницу',
    errorHint: 'Произошла непредвиденная ошибка. Перезагрузите страницу или вернитесь на главную.',
    home: 'На главную',
    retry: 'Попробовать снова',
    note: 'Каждый маленький шаг — новая возможность.',
    language: 'Выбрать язык',
    light: 'Светлая тема',
    dark: 'Тёмная тема',
    theme: 'Тема',
  },
  en: {
    notFound: 'This page could not be found',
    notFoundHint:
      'This address may have changed or the page is not available yet. Continue your path of learning and worship from home.',
    error: 'This page could not open',
    errorHint: 'Something unexpected happened. Reload the page or return home to continue.',
    home: 'Back to home',
    retry: 'Try again',
    note: 'Every small step is a new opportunity.',
    language: 'Select language',
    light: 'Light appearance',
    dark: 'Dark appearance',
    theme: 'Appearance',
  },
};

export const readFailureMode = (): 'light' | 'dark' => {
  if (typeof document !== 'undefined') {
    const value = document.documentElement.getAttribute('data-color-scheme');
    if (value === 'light' || value === 'dark') return value;
  }
  if (typeof window !== 'undefined') {
    try {
      const value = window.localStorage.getItem('theme-mode');
      if (value === 'light' || value === 'dark') return value;
    } catch {
      /* Theme storage can be unavailable in privacy mode. */
    }
    if (window.matchMedia?.('(prefers-color-scheme: dark)').matches) return 'dark';
  }
  return 'light';
};
export const applyFailureMode = (mode: 'light' | 'dark') => {
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-color-scheme', mode);
    document.documentElement.style.colorScheme = mode;
  }
  if (typeof window !== 'undefined') {
    try {
      window.localStorage.setItem('theme-mode', mode);
    } catch {
      /* Rendering remains usable without storage. */
    }
  }
};
export const resolveFailureLanguage = (language?: string): FailureLanguage => {
  const value = language?.toLowerCase().split('-')[0];
  return value === 'ru' || value === 'en' ? value : 'uz';
};

function LearningArch() {
  return (
    <svg viewBox="0 0 360 250" aria-hidden="true" className="deenly-failure__art" fill="none">
      <ellipse cx="180" cy="226" rx="118" ry="14" fill="currentColor" opacity=".07" />
      <path
        d="M75 208V119c0-41 39-56 105-103 66 47 105 62 105 103v89"
        fill="currentColor"
        opacity=".06"
      />
      <path
        d="M98 206v-85c0-34 31-47 82-83 51 36 82 49 82 83v85"
        stroke="currentColor"
        strokeWidth="1.5"
        opacity=".3"
      />
      <path
        d="M118 211v-82c0-28 22-37 62-65 40 28 62 37 62 65v82"
        stroke="currentColor"
        strokeWidth="1.5"
        opacity=".14"
      />
      <path
        d="M99 171c27-10 54-4 81 11 27-15 54-21 81-11v47c-27-10-54-4-81 11-27-15-54-21-81-11Z"
        fill="var(--failure-paper)"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M180 182v47m-62-42c17-2 33 1 46 7m-46 9c17-2 33 1 46 7m78-23c-17-2-33 1-46 7m46 9c-17-2-33 1-46 7"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        opacity=".55"
      />
      <path
        d="m40 98 4-10 4 10 10 4-10 4-4 10-4-10-10-4Zm271 57 3-7 3 7 7 3-7 3-3 7-3-7-7-3Z"
        fill="currentColor"
        opacity=".4"
      />
      <circle cx="306" cy="69" r="3" fill="currentColor" opacity=".3" />
      <circle cx="54" cy="176" r="2" fill="currentColor" opacity=".3" />
      <path
        d="M205 87a15 15 0 0 1-19-19 16 16 0 1 0 19 19Z"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
  );
}

const styles = `
body:has(.deenly-failure) { margin: 0; }
.deenly-failure { --failure-bg: #fcfdfd; --failure-paper: #fff; --failure-text: #1c252e; --failure-muted: #637381; --failure-accent: #008c68; --failure-soft: #eef8f3; box-sizing: border-box; width: 100%; height: 100dvh; min-height: 0; padding: 16px 20px; overflow: auto; display: flex; flex-direction: column; color: var(--failure-text); background: var(--failure-bg); font-family: "Public Sans Variable", Arial, sans-serif; }
.deenly-failure__card { max-width: 720px; width: 100%; box-sizing: border-box; margin: auto; flex-shrink: 0; padding: clamp(20px,3vw,40px); border-radius: 24px; background: var(--failure-paper); text-align: center; box-shadow: 0 4px 12px -2px rgba(145,158,171,.08),0 12px 28px -4px rgba(145,158,171,.12); }
.deenly-failure__art { width: min(100%,260px); height: min(18dvh,170px); display: block; margin: 0 auto 8px; color: var(--failure-accent); }
.deenly-failure__code { display: inline-block; padding: 6px 14px; background: var(--failure-soft); color: var(--failure-accent); font-size: 13px; font-weight: 600; border-radius: 8px; letter-spacing: 2px; }
.deenly-failure h1 { margin: 14px 0 10px; font-family: Barlow,"Public Sans Variable",Arial,sans-serif; font-size: clamp(26px,3vw,36px); font-weight: 600; line-height: 1.2; outline: none; }
.deenly-failure__hint { max-width: 520px; margin: 0 auto; color: var(--failure-muted); line-height: 1.65; font-size: 14px; }
.deenly-failure__actions { max-width: 420px; margin: 20px auto 16px; display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
.deenly-failure__action { display: inline-flex; align-items: center; justify-content: center; flex: 1 1 120px; min-width: 0; gap: 7px; min-height: 44px; padding: 8px 10px; box-sizing: border-box; border: 1px solid var(--failure-accent); border-radius: 10px; background: transparent; color: var(--failure-accent); text-decoration: none; font: 600 13px/1.4 "Public Sans Variable",Arial,sans-serif; cursor: pointer; }
.deenly-failure__action:hover { background: var(--failure-soft); }
.deenly-failure__action svg { width: 19px; height: 19px; flex-shrink: 0; }
.deenly-failure__action:focus-visible { outline: 3px solid var(--failure-accent); outline-offset: 4px; }
.deenly-failure__note { font-size: 13px; color: var(--failure-muted); margin: 0; }
.deenly-failure__controls { display: flex; justify-content: center; align-items: center; gap: 8px; margin-top: 16px; }
.deenly-failure__group { display: flex; gap: 2px; }
.deenly-failure__control { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 34px; padding: 4px; border: 0; border-radius: 8px; background: transparent; color: var(--failure-muted); cursor: pointer; font: 500 12px "Public Sans Variable",Arial,sans-serif; }
.deenly-failure__control[aria-pressed="true"] { color: var(--failure-accent); background: var(--failure-soft); }
.deenly-failure__control svg { width: 19px; height: 19px; }
.deenly-failure__control:focus-visible { outline: 2px solid var(--failure-accent); outline-offset: 2px; }
@media (max-height:650px) { .deenly-failure__art { height: min(14dvh,100px); } .deenly-failure__card { padding: 20px; } .deenly-failure h1 { margin-top: 10px; } }
[data-color-scheme="dark"] .deenly-failure { --failure-bg: #141a21; --failure-paper: #1c252e; --failure-text: #f4f6f8; --failure-muted: #a4b0bb; --failure-accent: #67d0b6; --failure-soft: #203b35; }
[data-color-scheme="dark"] .deenly-failure__card { box-shadow: 0 4px 12px -2px rgba(0,0,0,.12),0 12px 28px -4px rgba(0,0,0,.2); }
@media (prefers-color-scheme:dark) { html:not([data-color-scheme="light"]) .deenly-failure { --failure-bg: #141a21; --failure-paper: #1c252e; --failure-text: #f4f6f8; --failure-muted: #a4b0bb; --failure-accent: #67d0b6; --failure-soft: #203b35; } }
`;

/** This fallback is intentionally independent of Theme, Router, Locale and query providers. */
export function FailurePage({
  kind,
  language,
  onRetry,
}: {
  kind: '404' | 'error';
  language?: FailureLanguage;
  onRetry?: () => void;
}) {
  const [currentLanguage, setCurrentLanguage] = useState<FailureLanguage>(
    () =>
      language ??
      resolveFailureLanguage(
        typeof document === 'undefined' ? undefined : document.documentElement.lang
      )
  );
  const [mode, setMode] = useState(readFailureMode);
  useEffect(() => {
    if (language) setCurrentLanguage(language);
  }, [language]);
  const labels = failureLabels[currentLanguage];
  useEffect(() => {
    document.title = `${kind === '404' ? labels.notFound : labels.error} | Deenly.uz`;
  }, [kind, labels]);
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    heading.current?.focus({ preventScroll: true });
  }, []);
  return (
    <main lang={currentLanguage} className="deenly-failure">
      <style>{styles}</style>
      <section className="deenly-failure__card" aria-labelledby="deenly-failure-title">
        <LearningArch />
        <span className="deenly-failure__code">{kind === '404' ? '404' : 'DEENLY'}</span>
        <h1 id="deenly-failure-title" ref={heading} tabIndex={-1}>
          {kind === '404' ? labels.notFound : labels.error}
        </h1>
        <p className="deenly-failure__hint">
          {kind === '404' ? labels.notFoundHint : labels.errorHint}
        </p>
        <div className="deenly-failure__actions">
          <a href="/" className="deenly-failure__action">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="m3 10 9-7 9 7v10H3V10Zm6 10v-7h6v7"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            {labels.home}
          </a>
          <button
            type="button"
            className="deenly-failure__action"
            onClick={onRetry ?? (() => window.location.reload())}
          >
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M20 9a8 8 0 1 0 .5 6M20 4v5h-5"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            {labels.retry}
          </button>
        </div>
        <p className="deenly-failure__note">{labels.note}</p>
        <div className="deenly-failure__controls">
          <div className="deenly-failure__group" role="group" aria-label={labels.theme}>
            <button
              type="button"
              className="deenly-failure__control"
              aria-label={labels.light}
              aria-pressed={mode === 'light'}
              onClick={() => {
                setMode('light');
                applyFailureMode('light');
              }}
            >
              <svg viewBox="0 0 24 24" aria-hidden="true" fill="none">
                <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.5" />
                <path
                  d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M19 5l-1.5 1.5m-11 11L5 19"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </button>
            <button
              type="button"
              className="deenly-failure__control"
              aria-label={labels.dark}
              aria-pressed={mode === 'dark'}
              onClick={() => {
                setMode('dark');
                applyFailureMode('dark');
              }}
            >
              <svg viewBox="0 0 24 24" aria-hidden="true" fill="none">
                <path
                  d="M20 14A8 8 0 0 1 10 4a9 9 0 1 0 10 10Z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
          <div className="deenly-failure__group" role="group" aria-label={labels.language}>
            {(['uz', 'ru', 'en'] as const).map((value) => (
              <button
                key={value}
                type="button"
                className="deenly-failure__control"
                aria-label={{ uz: 'O‘zbekcha', ru: 'Русский', en: 'English' }[value]}
                aria-pressed={currentLanguage === value}
                onClick={() => {
                  setCurrentLanguage(value);
                  if (typeof document !== 'undefined') document.documentElement.lang = value;
                }}
              >
                {value.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
