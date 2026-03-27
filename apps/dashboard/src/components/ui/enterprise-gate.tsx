'use client';

import { Button, Card, CardContent } from '@encypher/design-system';
import Link from 'next/link';

export interface EnterpriseGateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  features: string[];
}

export function EnterpriseGate({ icon, title, description, features }: EnterpriseGateProps) {
  return (
    <Card>
      <CardContent className="py-12">
        <div className="max-w-2xl mx-auto text-center">
          <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-blue-ncs/10 flex items-center justify-center">
            {icon}
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-3">{title}</h2>
          <p className="text-muted-foreground mb-8 max-w-lg mx-auto">{description}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8 text-left max-w-lg mx-auto">
            {features.map((f) => (
              <div key={f} className="flex items-start gap-3">
                <svg className="w-5 h-5 text-blue-ncs mt-0.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 6L9 17l-5-5"/>
                </svg>
                <span className="text-sm text-foreground">{f}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-center gap-3">
            <Link href="/billing">
              <Button variant="primary">Upgrade to Enterprise</Button>
            </Link>
            <a href="mailto:sales@encypher.com">
              <Button variant="outline">Talk to Sales</Button>
            </a>
          </div>
          <p className="text-xs text-muted-foreground mt-4">Available on Enterprise plan</p>
        </div>
      </CardContent>
    </Card>
  );
}
