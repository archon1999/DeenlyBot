import { LazyMotion, domAnimation } from 'framer-motion';

// ----------------------------------------------------------------------

export type MotionLazyProps = {
  children: React.ReactNode;
};

export function MotionLazy({ children }: MotionLazyProps) {
  return (
    <LazyMotion strict features={domAnimation}>
      {children}
    </LazyMotion>
  );
}
