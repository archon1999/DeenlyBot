import type { UserSettings } from '../domain';

import { useRef, useState, useEffect } from 'react';

export function reconcileSettingsDraft(
  draft: UserSettings,
  previous: UserSettings,
  incoming: UserSettings
): UserSettings {
  return Object.fromEntries(
    (Object.keys(incoming) as (keyof UserSettings)[]).map((key) => [
      key,
      draft[key] === previous[key] ? incoming[key] : draft[key],
    ])
  ) as UserSettings;
}

export function useSettingsDraft(initial: UserSettings) {
  const [values, setValues] = useState(initial);
  const snapshot = useRef(initial);
  useEffect(() => {
    const previous = snapshot.current;
    snapshot.current = initial;
    setValues((draft) => reconcileSettingsDraft(draft, previous, initial));
  }, [initial]);
  return { values, setValues };
}
