import { useRef, useState, useEffect } from 'react';

export function useProfileNameDraft(firstName: string) {
  const [name, setName] = useState(firstName);
  const snapshot = useRef(firstName);
  useEffect(() => {
    const previous = snapshot.current;
    snapshot.current = firstName;
    setName((current) => (current === previous ? firstName : current));
  }, [firstName]);
  return { name, setName };
}
