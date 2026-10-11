import type { IconifyJSON } from '@iconify/react';
import type allIcons from './icon-sets';

import { addCollection } from '@iconify/react';

import coreIcons from './core-icon-sets';

export type IconifyName = keyof typeof allIcons | keyof typeof coreIcons;

function collections(icons: Record<string, { body: string }>): IconifyJSON[] {
  const groups = new Map<string, IconifyJSON>();
  Object.entries(icons).forEach(([key, value]) => {
    const [prefix, name] = key.split(':');
    const collection = groups.get(prefix) ?? { prefix, icons: {} };
    collection.icons[name] = value;
    groups.set(prefix, collection);
  });
  return [...groups.values()];
}

export const iconSets = collections(coreIcons);
export const allIconNames = Object.keys(coreIcons) as IconifyName[];
let coreRegistered = false;
let catalogueRegistered = false;
let cataloguePromise: Promise<void> | undefined;

function registerCollections(sets: IconifyJSON[]) {
  sets.forEach((set) => {
    const size = set.prefix === 'carbon' ? 32 : 24;
    addCollection({ ...set, width: size, height: size });
  });
}

export function registerIcons() {
  if (!coreRegistered) {
    registerCollections(iconSets);
    coreRegistered = true;
  }
}

export function hasRegisteredIcon(name: IconifyName) {
  return catalogueRegistered || allIconNames.includes(name);
}

export function loadIconCatalogue() {
  cataloguePromise ??= import('./icon-sets').then(({ default: catalogue }) => {
    registerCollections(collections(catalogue));
    catalogueRegistered = true;
  });
  return cataloguePromise;
}
