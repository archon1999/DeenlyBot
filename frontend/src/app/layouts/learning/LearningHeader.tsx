import type { NavSectionProps } from 'src/shared/ui/nav-section';

import { Stack, Tooltip, IconButton } from '@mui/material';

import { Logo } from 'src/shared/ui/logo';
import { useLocale } from 'src/shared/i18n';
import { usePathname } from 'src/app/routes/hooks';
import { RouterLink } from 'src/app/routes/components';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

import { HeaderSection } from '../core';
import { Searchbar } from '../components/searchbar';
import { isNavItemSelected } from './navigation-state';
import { DesktopNavigation } from './DesktopNavigation';
import { AccountMenu } from '../components/account-menu';
import { ThemeButton } from '../components/theme-button';
import { LanguagePopover } from '../components/language-popover';

export function LearningHeader({
  data,
  onOpenMenu,
  menuOpen,
}: {
  data: NavSectionProps['data'];
  onOpenMenu: () => void;
  menuOpen: boolean;
}) {
  const { language } = useLocale();
  const pathname = usePathname();
  const shortcuts = data
    .flatMap((group) => group.items)
    .filter((item) => ['/calendar', '/reports'].includes(item.path));
  const openLabel = { uz: 'Menyuni ochish', ru: 'Открыть меню', en: 'Open menu' }[language];
  return (
    <HeaderSection
      disableOffset
      disableElevation
      slotProps={{ container: { maxWidth: 'xl', sx: { px: { xs: 2, sm: 3 } } } }}
      slots={{
        leftArea: (
          <Stack direction="row" spacing={{ xs: 1, sm: 2 }} alignItems="center" flexShrink={0}>
            <IconButton
              aria-label={openLabel}
              aria-haspopup="dialog"
              aria-expanded={menuOpen}
              aria-controls={menuOpen ? 'learning-navigation-sheet' : undefined}
              onClick={onOpenMenu}
              sx={{ ml: -1, '@media (min-width:1340px)': { display: 'none' } }}
            >
              <OutlineIcon name="menu" width={22} />
            </IconButton>
            <Logo
              isSingle={false}
              sx={{
                gap: { xs: 1, sm: 1.25 },
                '& svg': { width: { xs: 30, sm: 36 }, height: { xs: 30, sm: 36 } },
                '& .MuiTypography-root': { fontSize: { xs: 17, sm: 21 } },
                '& .MuiTypography-root span': { display: { xs: 'none', sm: 'inline' } },
                '@media (max-width:359px)': { '& .MuiTypography-root': { display: 'none' } },
              }}
            />
          </Stack>
        ),
        centerArea: <DesktopNavigation data={data} />,
        rightArea: (
          <Stack direction="row" spacing={{ xs: 0, sm: 0.5 }} alignItems="center" flexShrink={0}>
            <Searchbar data={data} />
            <ThemeButton />
            {shortcuts.map((item) => (
              <Tooltip key={item.path} title={item.title}>
                <IconButton
                  component={RouterLink}
                  href={item.path}
                  aria-label={item.title}
                  aria-current={isNavItemSelected(pathname, item.path) ? 'page' : undefined}
                  sx={{
                    display: { xs: 'none', sm: 'inline-flex' },
                    color: isNavItemSelected(pathname, item.path) ? 'primary.main' : undefined,
                  }}
                >
                  <OutlineIcon
                    name={item.path === '/calendar' ? 'calendar' : 'reports'}
                    width={22}
                  />
                </IconButton>
              </Tooltip>
            ))}
            <LanguagePopover />
            <AccountMenu />
          </Stack>
        ),
      }}
      sx={(theme) => ({
        borderBottom: `1px solid ${theme.vars.palette.divider}`,
        bgcolor: 'background.paper',
        '&::before': { display: 'none' },
      })}
    />
  );
}
