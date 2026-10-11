import { useId, useState } from 'react';
import { useNavigate } from 'react-router';

import {
  Box,
  Chip,
  Menu,
  Alert,
  Stack,
  Button,
  Divider,
  MenuItem,
  Typography,
} from '@mui/material';

import { RouterLink } from 'src/app/routes/components';
import { OutlineIcon } from 'src/shared/ui/outline-icon';
import { useSession } from 'src/modules/auth/application';
import { useAuthLabels } from 'src/modules/auth/ui/labels';

/** Flat anchored profile menu follows cp_uz LearningHeader/AccountMenu. */
export function AccountMenu() {
  const { profile, logout } = useSession();
  const labels = useAuthLabels();
  const navigate = useNavigate();
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const menuId = useId();
  const triggerId = useId();
  const name = profile?.isGuest
    ? labels.guest
    : profile?.firstName || profile?.username || profile?.email || labels.account;
  const close = () => setAnchor(null);
  const signOut = async () => {
    setBusy(true);
    setError(null);
    try {
      await logout();
      close();
      navigate('/', { replace: true });
    } catch (reason) {
      setError(reason);
    } finally {
      setBusy(false);
    }
  };
  const row = { gap: 1.5, py: 1.25, px: 1.5, fontWeight: 500 };
  return (
    <>
      <Button
        id={triggerId}
        aria-label={labels.account}
        aria-haspopup="menu"
        aria-expanded={Boolean(anchor)}
        aria-controls={anchor ? menuId : undefined}
        color="inherit"
        onClick={(event) => setAnchor(event.currentTarget)}
        sx={{
          minWidth: 40,
          minHeight: 38,
          gap: 0.75,
          px: { xs: 0.75, sm: 1.25 },
          border: { xs: 'none', lg: '1px solid' },
          borderColor: { lg: 'divider' },
          borderRadius: 1.5,
          fontWeight: 500,
        }}
      >
        <Typography
          variant="body2"
          noWrap
          sx={{
            maxWidth: { xs: 64, sm: 110 },
            fontWeight: 500,
          }}
        >
          {name}
        </Typography>
        <Box sx={{ display: 'inline-flex', flexShrink: 0 }}>
          <OutlineIcon name="down" width={14} />
        </Box>
      </Button>
      <Menu
        id={menuId}
        anchorEl={anchor}
        open={Boolean(anchor)}
        onClose={close}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        slotProps={{
          list: { 'aria-labelledby': triggerId },
          paper: {
            sx: {
              width: 272,
              maxWidth: 'calc(100vw - 32px)',
              mt: 1.5,
              overflow: 'visible',
              bgcolor: 'background.paper',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: -6,
                right: 16,
                width: 12,
                height: 12,
                bgcolor: 'background.paper',
                transform: 'rotate(45deg)',
                zIndex: -1,
              },
            },
          },
        }}
      >
        <Box sx={{ px: 2, py: 1.5 }}>
          <Stack spacing={0.75}>
            <Typography variant="body2" fontWeight={500}>
              {name}
            </Typography>
            {(profile?.email || profile?.username) && (
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ overflowWrap: 'anywhere' }}
              >
                {profile.email || `@${profile.username}`}
              </Typography>
            )}
            <Chip
              label={
                profile?.isGuest
                  ? labels.guest
                  : profile?.accountKind === 'telegram'
                    ? labels.telegramAccount
                    : labels.member
              }
              size="small"
              variant="soft"
              color={profile?.isGuest ? 'default' : 'primary'}
              sx={{ alignSelf: 'flex-start', fontWeight: 500 }}
            />
          </Stack>
        </Box>
        <Divider />
        <MenuItem component={RouterLink} href="/profile" onClick={close} sx={row}>
          <OutlineIcon name="user" width={20} />
          {labels.profileTitle}
        </MenuItem>
        {profile && !profile.telegramLinked && (
          <MenuItem component={RouterLink} href="/profile#telegram-link" onClick={close} sx={row}>
            <OutlineIcon name="telegram" width={20} />
            {labels.linkTitle}
          </MenuItem>
        )}
        <MenuItem component={RouterLink} href="/settings" onClick={close} sx={row}>
          <OutlineIcon name="settings" width={20} />
          {labels.settings}
        </MenuItem>
        <Divider />
        {profile?.isGuest ? (
          <MenuItem component={RouterLink} href="/login" onClick={close} sx={row}>
            <OutlineIcon name="login" width={20} />
            {labels.login}
          </MenuItem>
        ) : (
          <MenuItem disabled={busy} onClick={signOut} sx={{ ...row, color: 'error.main' }}>
            <OutlineIcon name="logout" width={20} />
            {labels.signOut}
          </MenuItem>
        )}
        {error instanceof Error && (
          <Box sx={{ px: 1.5, py: 1 }}>
            <Alert severity="error">{error.message}</Alert>
          </Box>
        )}
      </Menu>
    </>
  );
}
