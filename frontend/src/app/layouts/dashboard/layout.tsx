import type { Breakpoint } from '@mui/material/styles';
import type { NavSectionProps } from 'src/shared/ui/nav-section';
import type { MainSectionProps, HeaderSectionProps, LayoutSectionProps } from '../core';

import { lazy, useRef, Suspense, useState, useEffect } from 'react';

import { Box, Link } from '@mui/material';
import GlobalStyles from '@mui/material/GlobalStyles';

import { useLocale } from 'src/shared/i18n';
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
  const { language } = useLocale();
  const pathname = usePathname();
  const contentRef = useRef<HTMLElement>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const defaultNavData = useNavData();
  const navData = slotProps?.nav?.data ?? defaultNavData;
  useEffect(() => {
    setMobileOpen(false);
    contentRef.current?.scrollTo({ top: 0, left: 0 });
  }, [pathname]);
  return (
    <MotionLazy>
      <GlobalStyles
        styles={{ 'body, #root': { height: '100dvh', minHeight: 0, overflow: 'hidden' } }}
      />
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
        sx={[
          { height: '100dvh', minHeight: 0, overflow: 'hidden' },
          ...(Array.isArray(sx) ? sx : [sx]),
        ]}
      >
        <MainSection
          {...slotProps?.main}
          ref={contentRef}
          id="main-content"
          tabIndex={0}
          sx={[
            {
              minHeight: 0,
              minWidth: 0,
              overflowY: 'auto',
              overflowX: 'hidden',
              overscrollBehaviorY: 'contain',
              scrollbarGutter: 'stable',
            },
            ...(Array.isArray(slotProps?.main?.sx) ? slotProps.main.sx : [slotProps?.main?.sx]),
          ]}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              flexShrink: 0,
              minHeight: {
                xs: 'calc(100dvh - var(--layout-header-mobile-height))',
                lg: 'calc(100dvh - var(--layout-header-desktop-height))',
              },
            }}
          >
            {children}
          </Box>
          <Box component="footer" sx={{ px: 3, pb: 3, textAlign: 'center' }}>
            <Link href={`/learn/${language}/`} underline="hover" sx={{ display: 'inline-block', p: 1.5 }}>
              {{ uz: 'Deenly ochiq o‘quv kutubxonasi', ru: 'Открытая библиотека Deenly', en: 'Deenly public learning library' }[language]}
            </Link>
          </Box>
        </MainSection>
        <Suspense fallback={null}>
          {mobileOpen && <TopNavigation data={navData} onClose={() => setMobileOpen(false)} />}
        </Suspense>
      </LayoutSection>
    </MotionLazy>
  );
}
