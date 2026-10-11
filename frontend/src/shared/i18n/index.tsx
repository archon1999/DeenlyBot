import { useState, useEffect, useContext, createContext } from 'react';

export type Language = 'uz' | 'ru' | 'en';
type LocaleValue = { language: Language; setLanguage: (value: Language) => void };
const LocaleContext = createContext<LocaleValue | null>(null);
export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>('uz');
  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);
  return (
    <LocaleContext.Provider value={{ language, setLanguage }}>{children}</LocaleContext.Provider>
  );
}
export function useLocale() {
  const value = useContext(LocaleContext);
  if (!value) throw new Error('LocaleProvider is missing');
  return value;
}
