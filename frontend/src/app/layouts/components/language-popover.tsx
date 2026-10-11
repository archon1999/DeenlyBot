import { useId, useState } from 'react';

import { Menu, Alert, MenuItem, IconButton } from '@mui/material';

import { FlagIcon } from 'src/shared/ui/flag-icon';
import { useLocale, type Language } from 'src/shared/i18n';
import { useLanguagePreference } from 'src/modules/auth/application';

const languages = [
  { value: 'en', label: 'English', country: 'GB' },
  { value: 'ru', label: 'Русский', country: 'RU' },
  { value: 'uz', label: 'O‘zbekcha', country: 'UZ' },
] as const;
export function LanguagePopover({ persist = true }: { persist?: boolean }) {
  const { language, setLanguage } = useLocale();
  const mutation = useLanguagePreference();
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);
  const menuId = useId();
  const currentLanguage = languages.find((item) => item.value === language)!;
  const change = (value: Language) => {
    setAnchor(null);
    if (persist) mutation.mutate(value);
    else setLanguage(value);
  };
  return (
    <>
      <IconButton
        color="inherit"
        aria-label={{ uz: 'Tilni tanlash', ru: 'Выбрать язык', en: 'Select language' }[language]}
        aria-haspopup="menu"
        aria-expanded={Boolean(anchor)}
        aria-controls={anchor ? menuId : undefined}
        onClick={(event) => setAnchor(event.currentTarget)}
        disabled={mutation.isPending}
        sx={{ width: 40, height: 40, bgcolor: anchor ? 'action.selected' : undefined }}
      >
        <FlagIcon code={currentLanguage.country} aria-hidden sx={{ width: 28, height: 20 }} />
      </IconButton>
      <Menu
        id={menuId}
        anchorEl={anchor}
        open={Boolean(anchor)}
        onClose={() => setAnchor(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        slotProps={{
          paper: {
            sx: {
              width: 220,
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
        {languages.map((item) => (
          <MenuItem
            key={item.value}
            selected={item.value === language}
            onClick={() => change(item.value)}
            sx={{ gap: 1.5, py: 1.25, px: 1.5 }}
          >
            <FlagIcon code={item.country} aria-hidden sx={{ width: 28, height: 20 }} />
            {item.label}
          </MenuItem>
        ))}
      </Menu>
      {mutation.error && (
        <Alert
          severity="error"
          onClose={() => mutation.reset()}
          sx={{ position: 'fixed', top: 80, right: 24 }}
        >
          {mutation.error.message}
        </Alert>
      )}
    </>
  );
}
