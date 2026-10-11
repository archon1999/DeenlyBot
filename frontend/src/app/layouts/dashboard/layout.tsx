import type { Breakpoint } from '@mui/material/styles';
import type { NavSectionProps } from 'src/shared/ui/nav-section';
import type { MainSectionProps, HeaderSectionProps, LayoutSectionProps } from '../core';

import { lazy, Suspense, useState, useEffect } from 'react';

import { usePathname } from 'src/app/routes/hooks';
import { MotionLazy } from 'src/shared/ui/animate/motion-lazy';

import { useNavData } from '../nav-config-dashboard';
import { MainSection, LayoutSection } from '../core';
import { LearningHeader } from '../learning/LearningHeader';

const TopNavigation = lazy(() =>
  import('../learning/TopNavigation').then((module) => ({ default: module.TopNavigation }))
);

export type DashboardLayoutProps = Pick<LayoutSectionProps, 'sx' | 'children' | 'cssVars'> & {
  layoutQuery?: Breakpoint;
  slotProps?: {
    header?: HeaderSectionProps;
    nav?: { data?: NavSectionProps['data'] };
    main?: MainSectionProps;
  };
};

export function DashboardLayout({ sx, cssVars, children, slotProps }: DashboardLayoutProps) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const defaultNavData = useNavData();
  const navData = slotProps?.nav?.data ?? defaultNavData;
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);
  return (
    <MotionLazy>
      <LayoutSection
        headerSection={
          <LearningHeader
            data={navData}
            onOpenMenu={() => setMobileOpen(true)}
            menuOpen={mobileOpen}
          />
        }
        cssVars={{
          '--layout-dashboard-content-pt': '32px',
          '--layout-dashboard-content-pb': '64px',
          '--layout-dashboard-content-px': '24px',
          ...cssVars,
        }}
        sx={[{ minHeight: '100vh' }, ...(Array.isArray(sx) ? sx : [sx])]}
      >
        <MainSection id="main-content" {...slotProps?.main}>
          {children}
        </MainSection>
        <Suspense fallback={null}>
          {mobileOpen && <TopNavigation data={navData} onClose={() => setMobileOpen(false)} />}
        </Suspense>
      </LayoutSection>
    </MotionLazy>
  );
}
