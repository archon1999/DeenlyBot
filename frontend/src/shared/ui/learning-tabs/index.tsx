import { varAlpha } from 'minimal-shared/utils';

import { Tab, Tabs } from '@mui/material';

/** Scrollable, light-mint navigation shared by learning readers and collections. */
export function LearningTabs({
  value,
  items,
  onChange,
  label,
}: {
  value: string;
  items: { key: string; title: string }[];
  onChange: (value: string) => void;
  label: string;
}) {
  return (
    <Tabs
      aria-label={label}
      value={value}
      onChange={(_, next) => onChange(next)}
      variant="scrollable"
      scrollButtons="auto"
      allowScrollButtonsMobile
      sx={{
        minHeight: 48,
        '& .MuiTabs-indicator': { display: 'none' },
        '& .MuiTabs-list': { gap: 1 },
        '& .MuiTab-root': {
          px: 2,
          minHeight: 44,
          borderRadius: 1.5,
          fontWeight: 500,
          whiteSpace: 'nowrap',
        },
      }}
    >
      {items.map((item) => (
        <Tab
          key={item.key}
          value={item.key}
          label={item.title}
          sx={(theme) => ({
            '&.Mui-selected': {
              bgcolor: varAlpha(theme.vars.palette.primary.mainChannel, 0.08),
              color: 'primary.main',
            },
            ...theme.applyStyles('dark', {
              '&.Mui-selected': {
                bgcolor: varAlpha(theme.vars.palette.primary.mainChannel, 0.16),
                color: 'primary.light',
              },
            }),
          })}
        />
      ))}
    </Tabs>
  );
}
