import type { IconifyProps } from 'src/shared/ui/iconify';

import { Iconify } from 'src/shared/ui/iconify';

const paths = {
  search: 'solar:magnifer-linear',
  moon: 'solar:moon-stars-linear',
  sun: 'solar:sun-2-linear',
  calendar: 'solar:calendar-mark-linear',
  reports: 'solar:documents-minimalistic-linear',
  menu: 'solar:hamburger-menu-linear',
  names: 'solar:notebook-bookmark-linear',
  arabic: 'solar:text-square-linear',
  library: 'solar:library-linear',
  qada: 'solar:checklist-minimalistic-linear',
  down: 'solar:alt-arrow-down-linear',
  close: 'solar:close-circle-linear',
  user: 'solar:user-circle-linear',
  guest: 'solar:user-circle-linear',
  login: 'solar:login-2-linear',
  logout: 'solar:logout-2-linear',
  settings: 'solar:settings-linear',
  telegram: 'solar:plane-2-linear',
  email: 'solar:letter-linear',
  lock: 'solar:lock-password-linear',
  link: 'solar:link-linear',
  check: 'solar:check-circle-linear',
  review: 'solar:restart-linear',
  'arrow-right': 'solar:arrow-right-linear',
} as const;

export type OutlineIconName = keyof typeof paths;

export function OutlineIcon({
  name,
  width = 24,
  ...other
}: Omit<IconifyProps, 'icon'> & { name: OutlineIconName }) {
  return <Iconify icon={paths[name]} width={width} {...other} />;
}
