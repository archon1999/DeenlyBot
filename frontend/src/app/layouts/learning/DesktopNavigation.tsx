import type { NavSectionProps } from 'src/shared/ui/nav-section';

import { varAlpha } from 'minimal-shared/utils';

import { Stack, Button } from '@mui/material';

import { useLocale } from 'src/shared/i18n';
import { usePathname } from 'src/app/routes/hooks';
import { RouterLink } from 'src/app/routes/components';

import { isNavItemSelected } from './navigation-state';

const primaryPaths = ['/names', '/arabic', '/library', '/qada'];
export function DesktopNavigation({ data }: { data: NavSectionProps['data'] }) {
  const { language } = useLocale();
  const pathname = usePathname();
  const allItems = data.flatMap((group) => group.items);
  const primary = allItems.filter((item) => primaryPaths.includes(item.path));
  return (
    <Stack
      component="nav"
      aria-label={{ uz: 'Asosiy menyu', ru: 'Главное меню', en: 'Main navigation' }[language]}
      direction="row"
      spacing={0.5}
      sx={{ display: 'none', '@media (min-width:1340px)': { display: 'flex' }, mx: 2 }}
    >
      {primary.map((item) => {
        const selected = isNavItemSelected(pathname, item.path);
        return (
          <Button
            key={item.path}
            component={RouterLink}
            href={item.path}
            aria-current={selected ? 'page' : undefined}
            size="small"
            color="inherit"
            startIcon={item.icon}
            sx={(theme) => ({
              px: 1.3,
              py: 0.875,
              minHeight: 40,
              fontWeight: 500,
              whiteSpace: 'nowrap',
              border: '1px solid transparent',
              color: selected ? 'primary.main' : 'text.secondary',
              bgcolor: selected
                ? varAlpha(theme.vars.palette.primary.mainChannel, 0.08)
                : 'transparent',
              '&:hover': {
                bgcolor: selected
                  ? varAlpha(theme.vars.palette.primary.mainChannel, 0.08)
                  : 'action.hover',
              },
              '& .MuiButton-startIcon > *': { width: 18, height: 18 },
              ...theme.applyStyles('dark', {
                bgcolor: selected ? 'primary.darker' : 'transparent',
                color: selected ? 'primary.lighter' : 'text.secondary',
                borderColor: selected ? 'primary.dark' : 'transparent',
                '&:hover': { bgcolor: selected ? 'primary.darker' : 'action.hover' },
              }),
            })}
          >
            {item.title}
          </Button>
        );
      })}
    </Stack>
  );
}
