import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'System Status - Encypher',
  description: 'Current operational status of Encypher services including API, signing, verification, and dashboard.',
};

// Revalidate every 60 seconds
export const revalidate = 60;

type ServiceStatus = {
  name: string;
  description: string;
  status: 'operational' | 'degraded' | 'down';
  responseTime?: number;
};

const serviceEndpoints = [
  { name: 'API Gateway', description: 'Core API routing and authentication', url: '/health' },
  { name: 'Authentication', description: 'User login, OAuth, and session management', url: '/health', port: 8001 },
  { name: 'Signing Service', description: 'Content signing with C2PA provenance', url: '/health', port: 8004 },
  { name: 'Verification Service', description: 'Provenance verification and validation', url: '/health', port: 8005 },
  { name: 'Coalition Network', description: 'Publisher coalition and licensing', url: '/health', port: 8009 },
  { name: 'Notifications', description: 'Webhooks and event delivery', url: '/health', port: 8008 },
];

async function checkService(endpoint: typeof serviceEndpoints[number]): Promise<ServiceStatus> {
  const baseUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = endpoint.port
    ? `http://localhost:${endpoint.port}${endpoint.url}`
    : `${baseUrl}${endpoint.url}`;

  try {
    const start = Date.now();
    const res = await fetch(url, {
      next: { revalidate: 60 },
      signal: AbortSignal.timeout(5000),
    });
    const responseTime = Date.now() - start;

    if (res.ok) {
      const data = await res.json();
      return {
        name: endpoint.name,
        description: endpoint.description,
        status: data.status === 'healthy' ? 'operational' : 'degraded',
        responseTime,
      };
    }
    return { name: endpoint.name, description: endpoint.description, status: 'degraded', responseTime };
  } catch {
    return { name: endpoint.name, description: endpoint.description, status: 'down' };
  }
}

function StatusDot({ status }: { status: ServiceStatus['status'] }) {
  const colors = {
    operational: 'bg-green-500',
    degraded: 'bg-yellow-500',
    down: 'bg-red-500',
  };
  const labels = {
    operational: 'Operational',
    degraded: 'Degraded',
    down: 'Unreachable',
  };
  const textColors = {
    operational: 'text-green-600 dark:text-green-400',
    degraded: 'text-yellow-600 dark:text-yellow-400',
    down: 'text-red-600 dark:text-red-400',
  };

  return (
    <div className="flex items-center gap-2">
      <span className="relative flex h-2.5 w-2.5">
        <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${colors[status]}`} />
      </span>
      <span className={`text-sm font-medium ${textColors[status]}`}>{labels[status]}</span>
    </div>
  );
}

export default async function StatusPage() {
  const results = await Promise.all(serviceEndpoints.map(checkService));
  const allOperational = results.every(r => r.status === 'operational');
  const anyDown = results.some(r => r.status === 'down');

  const overallStatus = allOperational ? 'operational' : anyDown ? 'down' : 'degraded';
  const overallLabel = {
    operational: 'All Systems Operational',
    degraded: 'Partial Degradation',
    down: 'Service Disruption',
  }[overallStatus];
  const overallBadgeStyles = {
    operational: 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800 text-green-700 dark:text-green-300',
    degraded: 'bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-300',
    down: 'bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300',
  }[overallStatus];
  const pingColor = {
    operational: 'bg-green-400',
    degraded: 'bg-yellow-400',
    down: 'bg-red-400',
  }[overallStatus];
  const dotColor = {
    operational: 'bg-green-500',
    degraded: 'bg-yellow-500',
    down: 'bg-red-500',
  }[overallStatus];

  return (
    <>
      <main className="min-h-[70vh] py-16 px-4">
        <div className="container max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border mb-6 ${overallBadgeStyles}`}>
              <span className="relative flex h-3 w-3">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${pingColor} opacity-75`} />
                <span className={`relative inline-flex rounded-full h-3 w-3 ${dotColor}`} />
              </span>
              <span className="text-sm font-medium">{overallLabel}</span>
            </div>
            <h1 className="text-4xl font-bold text-foreground mb-2">System Status</h1>
            <p className="text-muted-foreground">
              Live operational status of Encypher services. Updated every 60 seconds.
            </p>
          </div>

          <div className="bg-card rounded-xl border border-border overflow-hidden">
            {results.map((service, i) => (
              <div
                key={service.name}
                className={`flex items-center justify-between p-4 ${i < results.length - 1 ? 'border-b border-border' : ''}`}
              >
                <div>
                  <p className="font-medium text-foreground">{service.name}</p>
                  <p className="text-sm text-muted-foreground">{service.description}</p>
                </div>
                <div className="flex items-center gap-4">
                  {service.responseTime !== undefined && service.status === 'operational' && (
                    <span className="text-xs text-muted-foreground">{service.responseTime}ms</span>
                  )}
                  <StatusDot status={service.status} />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 text-center space-y-2">
            <p className="text-xs text-muted-foreground">
              Last checked: {new Date().toISOString().replace('T', ' ').slice(0, 19)} UTC
            </p>
            <p className="text-sm text-muted-foreground">
              For urgent issues, contact{' '}
              <a href="mailto:support@encypher.com" className="text-accent hover:underline">
                support@encypher.com
              </a>
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
