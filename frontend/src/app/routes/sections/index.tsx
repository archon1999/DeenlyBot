import type { RouteObject } from 'react-router';

import { lazy, Suspense } from 'react';
import { Outlet, Navigate, useLocation } from 'react-router';

import { Container } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { QueryState } from 'src/shared/ui/query-state';
import { FailurePage } from 'src/shared/ui/failure-page';
import { useSession } from 'src/modules/auth/application';
import { LoadingScreen } from 'src/shared/ui/loading-screen';

const LoginPage = lazy(() => import('src/modules/auth/ui').then((m) => ({ default: m.LoginPage })));
const ProfilePage = lazy(() =>
  import('src/modules/auth/ui').then((m) => ({ default: m.ProfilePage }))
);
const loadDashboardLayout = () =>
  import('src/app/layouts/dashboard/layout').then((m) => ({ default: m.DashboardLayout }));
const loadDashboardPage = () =>
  import('src/modules/dashboard').then((m) => ({ default: m.DashboardPage }));
const DashboardLayout = lazy(loadDashboardLayout);
const DashboardPage = lazy(loadDashboardPage);
// Download entry-view code during session discovery, without mounting private queries.
if (typeof window !== 'undefined' && window.location.pathname === '/') {
  void loadDashboardLayout().catch(() => undefined);
  void loadDashboardPage().catch(() => undefined);
}
const NamesPage = lazy(() => import('src/modules/names').then((m) => ({ default: m.NamesPage })));
const ArabicPage = lazy(() =>
  import('src/modules/arabic').then((m) => ({ default: m.ArabicPage }))
);
const LibraryPage = lazy(() =>
  import('src/modules/library').then((m) => ({ default: m.LibraryPage }))
);
const WorshipPage = lazy(() =>
  import('src/modules/worship').then((m) => ({ default: m.WorshipPage }))
);
const CalendarPage = lazy(() =>
  import('src/modules/calendar').then((m) => ({ default: m.CalendarPage }))
);
const ReportsPage = lazy(() =>
  import('src/modules/reports').then((m) => ({ default: m.ReportsPage }))
);
const SettingsPage = lazy(() =>
  import('src/modules/settings').then((m) => ({ default: m.SettingsPage }))
);
function ProtectedLayout() {
  const session = useSession();
  const location = useLocation();
  if (session.isLoading) return <LoadingScreen />;
  if (session.error)
    return (
      <Container sx={{ py: 10 }}>
        <QueryState isPending={false} error={session.error} onRetry={session.refreshSession}>
          {null}
        </QueryState>
      </Container>
    );
  if (!session.authenticated)
    return (
      <Navigate
        to={`/login?next=${encodeURIComponent(location.pathname + location.search)}`}
        replace
      />
    );
  return (
    <Suspense fallback={<LoadingScreen />}>
      <DashboardLayout>
        <Suspense fallback={<LoadingScreen />}>
          <Outlet />
        </Suspense>
      </DashboardLayout>
    </Suspense>
  );
}
function NotFound() {
  const { language } = useLocale();
  return <FailurePage kind="404" language={language} />;
}
export const routesSection: RouteObject[] = [
  {
    path: 'login',
    element: (
      <Suspense fallback={<LoadingScreen />}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    element: <ProtectedLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'names', element: <NamesPage /> },
      { path: 'arabic', element: <ArabicPage /> },
      { path: 'library', element: <LibraryPage /> },
      { path: 'qada', element: <WorshipPage /> },
      { path: 'worship', element: <Navigate to="/qada" replace /> },
      { path: 'calendar', element: <CalendarPage /> },
      { path: 'reports', element: <ReportsPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'profile', element: <ProfilePage /> },
    ],
  },
  // Missing pages must never inherit authentication gating or dashboard chrome.
  { path: '*', element: <NotFound /> },
];
