import type { ErrorInfo, ReactNode } from 'react';

import { Component } from 'react';

import { FailurePage } from 'src/shared/ui/failure-page';

export function ErrorBoundary() {
  return <FailurePage kind="error" />;
}

/** Catches failures of RouterProvider itself as well as providers outside route boundaries. */
export class AppErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    if (import.meta.env.DEV) console.error('Deenly render failed', error, info.componentStack);
  }
  render() {
    return this.state.failed ? <ErrorBoundary /> : this.props.children;
  }
}
