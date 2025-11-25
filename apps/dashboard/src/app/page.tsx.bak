'use client';

import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent, Input } from '@encypher/design-system';
import { useState } from 'react';

export default function DashboardPage() {
  const [apiKeys, setApiKeys] = useState([
    { id: '1', name: 'Production Key', key: 'ency_prod_**********************', created: '2025-01-15', lastUsed: '2 hours ago' },
    { id: '2', name: 'Development Key', key: 'ency_dev_**********************', created: '2025-01-10', lastUsed: '1 day ago' },
  ]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-white sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-lg" />
              <h1 className="text-xl font-bold text-delft-blue">Encypher Dashboard</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm">
                Documentation
              </Button>
              <Button variant="ghost" size="sm">
                Settings
              </Button>
              <div className="w-8 h-8 bg-columbia-blue rounded-full flex items-center justify-center text-white font-semibold">
                U
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">API Calls (30d)</div>
              <div className="text-3xl font-bold text-delft-blue">12,847</div>
              <div className="text-xs text-success mt-1">↑ 23% from last month</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Documents Signed</div>
              <div className="text-3xl font-bold text-delft-blue">3,421</div>
              <div className="text-xs text-success mt-1">↑ 15% from last month</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Verifications</div>
              <div className="text-3xl font-bold text-delft-blue">8,192</div>
              <div className="text-xs text-success mt-1">↑ 31% from last month</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Success Rate</div>
              <div className="text-3xl font-bold text-delft-blue">99.8%</div>
              <div className="text-xs text-muted-foreground mt-1">Last 30 days</div>
            </CardContent>
          </Card>
        </div>

        {/* API Keys Section */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>API Keys</CardTitle>
                <CardDescription>Manage your API keys for authentication</CardDescription>
              </div>
              <Button variant="primary">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Generate New Key
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {apiKeys.map((key) => (
                <div key={key.id} className="border border-border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="font-semibold text-delft-blue">{key.name}</h3>
                        <span className="px-2 py-1 bg-success/10 text-success text-xs rounded-full">Active</span>
                      </div>
                      <div className="font-mono text-sm text-muted-foreground mb-2">{key.key}</div>
                      <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                        <span>Created: {key.created}</span>
                        <span>•</span>
                        <span>Last used: {key.lastUsed}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </Button>
                      <Button variant="ghost" size="sm">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="w-12 h-12 bg-columbia-blue rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <CardTitle>Sign Document</CardTitle>
              <CardDescription>Add cryptographic signature to your content</CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="w-12 h-12 bg-blue-ncs rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <CardTitle>Verify Content</CardTitle>
              <CardDescription>Check authenticity of signed documents</CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="w-12 h-12 bg-rosy-brown rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <CardTitle>View Analytics</CardTitle>
              <CardDescription>Track usage and performance metrics</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </main>
    </div>
  );
}
