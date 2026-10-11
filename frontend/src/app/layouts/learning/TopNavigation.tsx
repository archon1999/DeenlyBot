import type { NavSectionProps } from 'src/shared/ui/nav-section';

import { useState } from 'react';
import { varAlpha } from 'minimal-shared/utils';

import {
  Box,
  List,
  Alert,
  Stack,
  Avatar,
  Button,
  Drawer,
  Divider,
  Container,
  IconButton,
  Typography,
  ListItemIcon,
  ListItemText,
  ListItemButton,
} from '@mui/material';

import { Logo } from 'src/shared/ui/logo';
import { useLocale } from 'src/shared/i18n';
import { usePathname } from 'src/app/routes/hooks';
import { RouterLink } from 'src/app/routes/components';
import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { useSession } from 'src/modules/auth/application';

import { isNavItemSelected } from './navigation-state';

export function TopNavigation({
  data,
  onClose,
}: {
  data: NavSectionProps['data'];
  onClose: () => void;
}) {
  const { language } = useLocale();
  const pathname = usePathname();
  const { profile, logout } = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const labels = {
    uz: { close: 'Menyuni yopish', nav: 'Menyu', settings: 'Sozlamalar', out: 'Hisobdan chiqish' },
    ru: { close: 'Закрыть меню', nav: 'Меню', settings: 'Настройки', out: 'Выйти' },
    en: { close: 'Close menu', nav: 'Navigation', settings: 'Settings', out: 'Sign out' },
  }[language];
  const signOut = async () => {
    setBusy(true);
    try {
      await logout();
      onClose();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };
  return (
    <Drawer
      anchor="top"
      open
      onClose={onClose}
      slotProps={{
        paper: {
          role: 'dialog',
          id: 'learning-navigation-sheet',
          'aria-modal': true,
          'aria-label': labels.nav,
          sx: {
            maxHeight: 'calc(100dvh - 16px)',
            borderRadius: '0 0 24px 24px',
            bgcolor: 'background.paper',
          },
        },
      }}
    >
      <Container maxWidth="md" sx={{ py: 2, pb: 'max(24px, env(safe-area-inset-bottom))' }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
          <Logo isSingle={false} />
          <IconButton aria-label={labels.close} onClick={onClose}>
            <OutlineIcon name="close" width={22} />
          </IconButton>
        </Stack>
        <Divider />
        <Box
          component="nav"
          aria-label={labels.nav}
          sx={{
            display: 'grid',
            gap: { xs: 2, sm: 4 },
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            py: 3,
          }}
        >
          {data.map((group, index) => (
            <Box key={group.subheader ?? index}>
              <Typography variant="overline" color="text.secondary" sx={{ px: 1.5 }}>
                {group.subheader}
              </Typography>
              <List disablePadding sx={{ mt: 1 }}>
                {group.items.map((item) => {
                  const selected = isNavItemSelected(pathname, item.path);
                  return (
                    <ListItemButton
                      key={item.path}
                      component={RouterLink}
                      href={item.path}
                      selected={selected}
                      aria-current={selected ? 'page' : undefined}
                      onClick={onClose}
                      sx={(theme) => ({
                        px: 1.5,
                        py: 1.2,
                        borderRadius: 1.5,
                        mb: 0.5,
                        color: selected ? 'primary.main' : 'text.primary',
                        '&.Mui-selected': {
                          bgcolor: varAlpha(theme.vars.palette.primary.mainChannel, 0.08),
                        },
                        '&.Mui-selected:hover': {
                          bgcolor: varAlpha(theme.vars.palette.primary.mainChannel, 0.08),
                        },
                        ...theme.applyStyles('dark', {
                          '&.Mui-selected': {
                            bgcolor: 'primary.darker',
                            color: 'primary.lighter',
                            boxShadow: `inset 0 0 0 1px ${theme.vars.palette.primary.dark}`,
                          },
                          '&.Mui-selected:hover': { bgcolor: 'primary.darker' },
                        }),
                      })}
                    >
                      <ListItemIcon sx={{ minWidth: 24, mr: 1.5, color: 'inherit' }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.title}
                        slotProps={{ primary: { variant: 'body2', fontWeight: 500 } }}
                      />
                    </ListItemButton>
                  );
                })}
              </List>
            </Box>
          ))}
        </Box>
        <Divider />
        <Stack direction="row" alignItems="center" spacing={2} sx={{ pt: 2.5 }}>
          <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main' }}>
            {profile?.firstName.charAt(0) || profile?.username.charAt(0)}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="subtitle2" noWrap>
              {profile?.firstName || profile?.username}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {profile?.timezone}
            </Typography>
          </Box>
          <Button color="inherit" size="small" disabled={busy} onClick={signOut}>
            {labels.out}
          </Button>
        </Stack>
        {error instanceof Error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error.message}
          </Alert>
        )}
      </Container>
    </Drawer>
  );
}
