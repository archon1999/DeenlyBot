import type { IconProps } from '@iconify/react';
import type { IconifyName } from './register-icons';

import { Icon } from '@iconify/react';
import { useId, useState, useEffect } from 'react';
import { mergeClasses } from 'minimal-shared/utils';

import { styled } from '@mui/material/styles';

import { iconifyClasses } from './classes';
import { registerIcons, hasRegisteredIcon, loadIconCatalogue } from './register-icons';

export type IconifyProps = React.ComponentProps<typeof IconRoot> &
  Omit<IconProps, 'icon'> & { icon: IconifyName };

export function Iconify({ className, icon, width = 20, height, sx, ...other }: IconifyProps) {
  const uniqueId = useId();
  registerIcons();
  const [ready, setReady] = useState(() => hasRegisteredIcon(icon));
  useEffect(() => {
    if (hasRegisteredIcon(icon)) {
      setReady(true);
      return undefined;
    }
    setReady(false);
    let active = true;
    loadIconCatalogue()
      .then(() => {
        if (active) setReady(true);
      })
      .catch(console.error);
    return () => {
      active = false;
    };
  }, [icon]);
  const styles = [
    { width, flexShrink: 0, height: height ?? width, display: 'inline-flex' },
    ...(Array.isArray(sx) ? sx : [sx]),
  ];
  const classes = mergeClasses([iconifyClasses.root, className]);
  // Wait for the local catalogue instead of fetching unknown icons from Iconify's API.
  if (!ready || !hasRegisteredIcon(icon))
    return <IconPlaceholder aria-hidden className={classes} sx={styles} />;
  return <IconRoot ssr id={uniqueId} icon={icon} className={classes} sx={styles} {...other} />;
}
const IconRoot = styled(Icon)``;
const IconPlaceholder = styled('span')``;
