'use client';

import React from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  LayoutDashboard,
  Users,
  Settings,
  FileText,
  Mail,
  BarChart,
  ArrowRight,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from 'lucide-react';

// UI Components
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@encypher/design-system';
import { Button } from '@encypher/design-system';

export default function AdminPage() {
  const { status } = useSession();
  const router = useRouter();

  // Redirect if not authenticated
  if (status === 'unauthenticated') {
    router.push('/auth/signin?callbackUrl=/admin');
    return null;
  }

  // Admin features
  const adminFeatures = [
    {
      title: 'Dashboard',
      description: 'View analytics and key metrics',
      icon: <LayoutDashboard className="h-6 w-6" />,
      href: '/admin/dashboard',
      color: 'bg-blue-500',
    },
    {
      title: 'Investor Requests',
      description: 'Manage investor access requests',
      icon: <Users className="h-6 w-6" />,
      href: '/admin/investor-requests',
      color: 'bg-green-500',
    },
    {
      title: 'Analytics',
      description: 'View detailed investor analytics',
      icon: <BarChart className="h-6 w-6" />,
      href: '/admin/analytics',
      color: 'bg-purple-500',
      disabled: true,
    },
    {
      title: 'Email Templates',
      description: 'Manage email notifications',
      icon: <Mail className="h-6 w-6" />,
      href: '/admin/email-templates',
      color: 'bg-amber-500',
      disabled: true,
    },
    {
      title: 'Content Management',
      description: 'Manage pitch deck content',
      icon: <FileText className="h-6 w-6" />,
      href: '/admin/content',
      color: 'bg-red-500',
      disabled: true,
    },
    {
      title: 'Settings',
      description: 'Configure admin preferences',
      icon: <Settings className="h-6 w-6" />,
      href: '/admin/settings',
      color: 'bg-gray-500',
      disabled: true,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Welcome to the Encypher admin dashboard. Manage investor access and monitor engagement.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {adminFeatures.map((feature) => (
          <Card key={feature.title} className={feature.disabled ? 'opacity-60' : ''}>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <div className={`p-2 rounded-md ${feature.color} text-white`}>
                  {feature.icon}
                </div>
                <CardTitle>{feature.title}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-sm">
                {feature.description}
              </CardDescription>
            </CardContent>
            <CardFooter>
              <Button
                variant="outline"
                className="w-full justify-between"
                asChild={!feature.disabled}
                disabled={feature.disabled}
              >
                {feature.disabled ? (
                  <span>
                    Coming Soon
                  </span>
                ) : (
                  <Link href={feature.href}>
                    Access {feature.title}
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Link>
                )}
              </Button>
            </CardFooter>
          </Card>
        ))}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Investor Requests</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">--</div>
                <p className="text-xs text-muted-foreground">Total requests</p>
              </div>
              <div className="flex gap-2">
                <div className="flex flex-col items-center">
                  <Clock className="h-4 w-4 text-amber-500" />
                  <span className="text-xs font-semibold">--</span>
                  <span className="text-xs text-muted-foreground">Pending</span>
                </div>
                <div className="flex flex-col items-center">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-xs font-semibold">--</span>
                  <span className="text-xs text-muted-foreground">Approved</span>
                </div>
                <div className="flex flex-col items-center">
                  <XCircle className="h-4 w-4 text-red-500" />
                  <span className="text-xs font-semibold">--</span>
                  <span className="text-xs text-muted-foreground">Rejected</span>
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button asChild variant="outline" size="sm" className="w-full">
              <Link href="/admin/investor-requests">View all requests</Link>
            </Button>
          </CardFooter>
        </Card>

        {/* Users Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">--</div>
            <p className="text-xs text-muted-foreground">Total registered users</p>
          </CardContent>
          <CardFooter>
            <Button asChild variant="outline" size="sm" className="w-full">
              <Link href="/admin/users">Manage users</Link>
            </Button>
          </CardFooter>
        </Card>

        {/* Email Notifications Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Email Notifications</CardTitle>
            <Mail className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Enabled</div>
            <p className="text-xs text-muted-foreground">Admin notifications are active</p>
          </CardContent>
          <CardFooter>
            <Button asChild variant="outline" size="sm" className="w-full">
              <Link href="/admin/settings">Configure settings</Link>
            </Button>
          </CardFooter>
        </Card>

        {/* Security Alerts Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">No active security alerts</p>
          </CardContent>
          <CardFooter>
            <Button asChild variant="outline" size="sm" className="w-full">
              <Link href="/admin/security">View security dashboard</Link>
            </Button>
          </CardFooter>
        </Card>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Button asChild variant="outline" className="h-20 flex flex-col items-center justify-center">
            <Link href="/admin/investor-requests?status=PENDING_APPROVAL">
              <Clock className="h-5 w-5 mb-1" />
              <span>Pending Approvals</span>
            </Link>
          </Button>
          <Button asChild variant="outline" className="h-20 flex flex-col items-center justify-center">
            <Link href="/admin/investor-requests/create">
              <Users className="h-5 w-5 mb-1" />
              <span>Add New Investor</span>
            </Link>
          </Button>
          <Button asChild variant="outline" className="h-20 flex flex-col items-center justify-center">
            <Link href="/admin/settings/email">
              <Mail className="h-5 w-5 mb-1" />
              <span>Email Settings</span>
            </Link>
          </Button>
          <Button asChild variant="outline" className="h-20 flex flex-col items-center justify-center">
            <Link href="/admin/help">
              <AlertTriangle className="h-5 w-5 mb-1" />
              <span>Help & Support</span>
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
