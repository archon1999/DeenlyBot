import 'src/global.css';

import { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { ApiError } from 'src/shared/api';
import { LocaleProvider } from 'src/shared/i18n';
import { ProgressBar } from 'src/shared/ui/progress-bar';
import { SessionProvider } from 'src/modules/auth/application';
import { defaultSettings, SettingsProvider } from 'src/shared/ui/settings';

import { usePathname } from './routes/hooks';
import { DocumentTitle } from './routes/components';
import { themeConfig, ThemeProvider } from './theme';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (count, error) => !(error instanceof ApiError && error.status < 500) && count < 1,
    },
    mutations: { retry: false },
  },
});
export default function App({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return (
    <QueryClientProvider client={queryClient}>
      <LocaleProvider>
        <DocumentTitle />
        <SessionProvider autoGuest={!/^\/login\/?$/.test(pathname)}>
          <SettingsProvider defaultSettings={defaultSettings}>
            <ThemeProvider
              modeStorageKey={themeConfig.modeStorageKey}
              defaultMode={themeConfig.defaultMode}
            >
              <ProgressBar />
              {children}
            </ThemeProvider>
          </SettingsProvider>
        </SessionProvider>
      </LocaleProvider>
    </QueryClientProvider>
  );
}
