'use client';

import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent } from '@encypher/design-system';
import { useState } from 'react';
import Link from 'next/link';
import { useSession } from 'next-auth/react';

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('30d');
  const { data: session } = useSession();
  const isAdmin = ((session?.user as any)?.role ?? '').toLowerCase() === 'admin';

  // Mock data - replace with actual API calls
  const stats = {
    totalCalls: 12847,
    totalSigned: 3421,
    totalVerified: 8192,
    successRate: 99.8,
    avgResponseTime: 145,
  };

  const recentActivity = [
    { id: 1, type: 'sign', document: 'contract_2025.pdf', timestamp: '2 minutes ago', status: 'success' },
    { id: 2, type: 'verify', document: 'invoice_jan.pdf', timestamp: '15 minutes ago', status: 'success' },
    { id: 3, type: 'sign', document: 'agreement.docx', timestamp: '1 hour ago', status: 'success' },
    { id: 4, type: 'verify', document: 'report_q4.pdf', timestamp: '2 hours ago', status: 'success' },
    { id: 5, type: 'sign', document: 'proposal.pdf', timestamp: '3 hours ago', status: 'failed' },
  ];

  const usageByDay = [
    { day: 'Mon', calls: 450 },
    { day: 'Tue', calls: 520 },
    { day: 'Wed', calls: 380 },
    { day: 'Thu', calls: 610 },
    { day: 'Fri', calls: 490 },
    { day: 'Sat', calls: 210 },
    { day: 'Sun', calls: 180 },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-white sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/">
                <div className="w-8 h-8 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-lg cursor-pointer" />
              </Link>
              <h1 className="text-xl font-bold text-delft-blue">Encypher Dashboard</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link href="/">
                <Button variant="ghost" size="sm">
                  Dashboard
                </Button>
              </Link>
              <Link href="/api-keys">
                <Button variant="ghost" size="sm">
                  API Keys
                </Button>
              </Link>
              <Link href="/settings">
                <Button variant="ghost" size="sm">
                  Settings
                </Button>
              </Link>
              <Link href="/billing">
                <Button variant="ghost" size="sm">
                  Billing
                </Button>
              </Link>
              {isAdmin && (
                <Link href="/admin">
                  <Button variant="ghost" size="sm">
                    Admin
                  </Button>
                </Link>
              )}
              <div className="w-8 h-8 bg-columbia-blue rounded-full flex items-center justify-center text-white font-semibold">
                {session?.user?.name?.charAt(0)?.toUpperCase() ?? 'U'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-delft-blue mb-2">Usage & Analytics</h2>
          <p className="text-muted-foreground">
            Track your API usage, performance metrics, and activity history
          </p>
        </div>

        {/* Time Range Selector */}
        <div className="flex items-center space-x-2 mb-6">
          <span className="text-sm text-muted-foreground">Time range:</span>
          {['7d', '30d', '90d', 'all'].map((range) => (
            <Button
              key={range}
              variant={timeRange === range ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setTimeRange(range)}
            >
              {range === 'all' ? 'All time' : `Last ${range}`}
            </Button>
          ))}
        </div>

        {/* Stats Overview */}
        <div className="grid md:grid-cols-5 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Total API Calls</div>
              <div className="text-3xl font-bold text-delft-blue">{stats.totalCalls.toLocaleString()}</div>
              <div className="text-xs text-success mt-1">↑ 23% vs previous period</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Documents Signed</div>
              <div className="text-3xl font-bold text-delft-blue">{stats.totalSigned.toLocaleString()}</div>
              <div className="text-xs text-success mt-1">↑ 15% vs previous period</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Verifications</div>
              <div className="text-3xl font-bold text-delft-blue">{stats.totalVerified.toLocaleString()}</div>
              <div className="text-xs text-success mt-1">↑ 31% vs previous period</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Success Rate</div>
              <div className="text-3xl font-bold text-delft-blue">{stats.successRate}%</div>
              <div className="text-xs text-muted-foreground mt-1">Last 30 days</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Avg Response</div>
              <div className="text-3xl font-bold text-delft-blue">{stats.avgResponseTime}ms</div>
              <div className="text-xs text-success mt-1">↓ 12ms vs previous</div>
            </CardContent>
          </Card>
        </div>

        {/* Usage Chart */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>API Calls by Day</CardTitle>
            <CardDescription>Daily API usage for the selected period</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between space-x-2">
              {usageByDay.map((day) => (
                <div key={day.day} className="flex-1 flex flex-col items-center">
                  <div 
                    className="w-full bg-columbia-blue rounded-t hover:bg-blue-ncs transition-colors cursor-pointer"
                    style={{ height: `${(day.calls / 700) * 100}%` }}
                    title={`${day.calls} calls`}
                  />
                  <div className="text-xs text-muted-foreground mt-2">{day.day}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest API requests and operations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        activity.type === 'sign' ? 'bg-columbia-blue' : 'bg-blue-ncs'
                      }`}>
                        {activity.type === 'sign' ? (
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                      </div>
                      <div>
                        <div className="font-medium text-sm">{activity.document}</div>
                        <div className="text-xs text-muted-foreground">{activity.timestamp}</div>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      activity.status === 'success' 
                        ? 'bg-success/10 text-success' 
                        : 'bg-destructive/10 text-destructive'
                    }`}>
                      {activity.status}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Top Documents */}
          <Card>
            <CardHeader>
              <CardTitle>Top Documents</CardTitle>
              <CardDescription>Most frequently signed/verified documents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: 'contract_template.pdf', count: 234, type: 'PDF' },
                  { name: 'invoice_template.docx', count: 189, type: 'DOCX' },
                  { name: 'agreement_v2.pdf', count: 156, type: 'PDF' },
                  { name: 'report_monthly.pdf', count: 142, type: 'PDF' },
                  { name: 'proposal.docx', count: 98, type: 'DOCX' },
                ].map((doc, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border border-border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-muted rounded flex items-center justify-center">
                        <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <div className="font-medium text-sm">{doc.name}</div>
                        <div className="text-xs text-muted-foreground">{doc.type}</div>
                      </div>
                    </div>
                    <div className="text-sm font-semibold text-delft-blue">{doc.count}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
