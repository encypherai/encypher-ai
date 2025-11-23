import { ReactNode } from 'react';

export default function PublisherDemoLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="publisher-demo-layout">
      {children}
    </div>
  );
}
