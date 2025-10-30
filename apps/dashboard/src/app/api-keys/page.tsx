'use client';

import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent, Input } from '@encypher/design-system';
import { useState } from 'react';

interface ApiKey {
  id: string;
  name: string;
  key: string;
  created: string;
  lastUsed: string;
  permissions: string[];
}

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    { 
      id: '1', 
      name: 'Production Key', 
      key: 'ency_prod_**********************', 
      created: '2025-01-15', 
      lastUsed: '2 hours ago',
      permissions: ['sign', 'verify', 'read']
    },
    { 
      id: '2', 
      name: 'Development Key', 
      key: 'ency_dev_**********************', 
      created: '2025-01-10', 
      lastUsed: '1 day ago',
      permissions: ['sign', 'verify']
    },
  ]);
  const [showNewKeyDialog, setShowNewKeyDialog] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [generatedKey, setGeneratedKey] = useState('');

  const handleGenerateKey = () => {
    // TODO: Replace with actual API call
    const newKey = {
      id: Date.now().toString(),
      name: newKeyName || 'Untitled Key',
      key: `ency_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`,
      created: new Date().toISOString().split('T')[0],
      lastUsed: 'Never',
      permissions: ['sign', 'verify', 'read']
    };
    
    setGeneratedKey(newKey.key);
    setApiKeys([...apiKeys, { ...newKey, key: `${newKey.key.substring(0, 10)}**********************` }]);
    setNewKeyName('');
  };

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key);
    // TODO: Show toast notification
  };

  const handleDeleteKey = (id: string) => {
    if (confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      setApiKeys(apiKeys.filter(k => k.id !== id));
      // TODO: Call API to delete key
    }
  };

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
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-delft-blue mb-2">API Keys</h2>
          <p className="text-muted-foreground">
            Manage your API keys for authentication. Keep your keys secure and never share them publicly.
          </p>
        </div>

        {/* Generate New Key Dialog */}
        {showNewKeyDialog && (
          <Card className="mb-6 border-columbia-blue">
            <CardHeader>
              <CardTitle>Generate New API Key</CardTitle>
              <CardDescription>
                {generatedKey ? 'Your new API key has been generated' : 'Create a new API key for your application'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {generatedKey ? (
                <div className="space-y-4">
                  <div className="bg-muted p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">Your new API key (save this now!):</p>
                    <div className="flex items-center space-x-2">
                      <code className="flex-1 bg-background px-3 py-2 rounded border border-border font-mono text-sm">
                        {generatedKey}
                      </code>
                      <Button variant="outline" size="sm" onClick={() => handleCopyKey(generatedKey)}>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </Button>
                    </div>
                  </div>
                  <div className="bg-warning/10 border border-warning p-4 rounded-lg">
                    <p className="text-sm text-warning-foreground">
                      <strong>Important:</strong> This is the only time you'll see this key. Make sure to copy it now and store it securely.
                    </p>
                  </div>
                  <Button variant="primary" onClick={() => { setShowNewKeyDialog(false); setGeneratedKey(''); }}>
                    Done
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label htmlFor="keyName" className="block text-sm font-medium text-foreground mb-2">
                      Key Name
                    </label>
                    <Input
                      id="keyName"
                      placeholder="e.g., Production API Key"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Give your key a descriptive name to help you identify it later
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="primary" onClick={handleGenerateKey}>
                      Generate Key
                    </Button>
                    <Button variant="outline" onClick={() => setShowNewKeyDialog(false)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* API Keys List */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Your API Keys</CardTitle>
                <CardDescription>{apiKeys.length} active key{apiKeys.length !== 1 ? 's' : ''}</CardDescription>
              </div>
              <Button variant="primary" onClick={() => setShowNewKeyDialog(true)}>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Generate New Key
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {apiKeys.length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 mx-auto text-muted-foreground mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
                <h3 className="text-lg font-semibold text-foreground mb-2">No API keys yet</h3>
                <p className="text-muted-foreground mb-4">Generate your first API key to get started</p>
                <Button variant="primary" onClick={() => setShowNewKeyDialog(true)}>
                  Generate Your First Key
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {apiKeys.map((key) => (
                  <div key={key.id} className="border border-border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-semibold text-delft-blue">{key.name}</h3>
                          <span className="px-2 py-1 bg-success/10 text-success text-xs rounded-full">Active</span>
                        </div>
                        <div className="font-mono text-sm text-muted-foreground mb-2">{key.key}</div>
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground mb-2">
                          <span>Created: {key.created}</span>
                          <span>•</span>
                          <span>Last used: {key.lastUsed}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          {key.permissions.map((perm) => (
                            <span key={perm} className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded">
                              {perm}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleCopyKey(key.key)}
                          title="Copy key"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleDeleteKey(key.id)}
                          title="Delete key"
                        >
                          <svg className="w-4 h-4 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Usage Tips */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Using Your API Keys</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-sm mb-2">Python SDK</h4>
                <pre className="bg-muted p-3 rounded-lg text-sm overflow-x-auto">
                  <code>{`from encypher_enterprise import EncypherClient

client = EncypherClient(api_key="your_api_key_here")
result = client.sign_document("document.pdf")`}</code>
                </pre>
              </div>
              <div>
                <h4 className="font-semibold text-sm mb-2">REST API</h4>
                <pre className="bg-muted p-3 rounded-lg text-sm overflow-x-auto">
                  <code>{`curl -X POST https://api.encypherai.com/v1/sign \\
  -H "Authorization: Bearer your_api_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{"document": "..."}'`}</code>
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
