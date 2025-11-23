import { ReactNode } from 'react';

export default function AIDemoLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="ai-demo-layout">
      {children}
    </div>
  );
}
