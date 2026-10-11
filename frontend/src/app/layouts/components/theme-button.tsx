import { Tooltip, IconButton } from '@mui/material';
import { useColorScheme } from '@mui/material/styles';

import { useLocale } from 'src/shared/i18n';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

export function ThemeButton() {
  const { mode, setMode } = useColorScheme();
  const { language } = useLocale();
  const label = {
    uz: 'Yorug‘/qorong‘i ko‘rinish',
    ru: 'Светлая/тёмная тема',
    en: 'Light/dark appearance',
  }[language];
  return (
    <Tooltip title={label}>
      <IconButton aria-label={label} onClick={() => setMode(mode === 'dark' ? 'light' : 'dark')}>
        <OutlineIcon name={mode === 'dark' ? 'sun' : 'moon'} width={22} />
      </IconButton>
    </Tooltip>
  );
}
