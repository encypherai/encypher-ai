"use client";

import { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Play, Loader2 } from 'lucide-react';

const sampleBodies = {
  sign: JSON.stringify({ text: "This is a test document to be signed." }, null, 2),
  verify: JSON.stringify({ text: "This is a test document to be verified with its signature..." }, null, 2),
};

export default function ApiSandbox() {
  const [endpoint, setEndpoint] = useState('sign');
  const [apiKey, setApiKey] = useState('');
  const [requestBody, setRequestBody] = useState(sampleBodies.sign);
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleEndpointChange = (value: string) => {
    setEndpoint(value);
    // @ts-ignore
    setRequestBody(sampleBodies[value]);
    setResponse('');
  };

  const handleRun = async () => {
    setIsLoading(true);
    setResponse('');
    try {
      const res = await fetch(`/api/v1/tools/${endpoint}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
          },
          body: requestBody,
        }
      );

      const data = await res.json();
      setResponse(JSON.stringify(data, null, 2));

    } catch (error: any) {
      setResponse(JSON.stringify({ error: error.message }, null, 2));
    } finally {
      setIsLoading(false);
    }
  };

  const codeSnippets = useMemo(() => {
    const getCurlSnippet = () => {
      return `curl -X POST ${window.location.origin}/api/v1/tools/${endpoint} \\\n     -H "Content-Type: application/json" \\\n     -H "Authorization: Bearer YOUR_API_KEY" \\\n     -d '${requestBody}'`;
    };

    const getPythonSnippet = () => {
      return `import requests\nimport json\n\nurl = "${window.location.origin}/api/v1/tools/${endpoint}"\nheaders = {\n    "Content-Type": "application/json",\n    "Authorization": "Bearer YOUR_API_KEY"\n}\npayload = ${requestBody}\n\nresponse = requests.post(url, headers=headers, data=json.dumps(payload))\nprint(response.json())`;
    };

    const getJsSnippet = () => {
      return `fetch("${window.location.origin}/api/v1/tools/${endpoint}", {\n  method: "POST",\n  headers: {\n    "Content-Type": "application/json",\n    "Authorization": "Bearer YOUR_API_KEY"\n  },\n  body: JSON.stringify(${requestBody})\n})\n.then(response => response.json())\n.then(data => console.log(data))\n.catch(error => console.error('Error:', error));`;
    };

    return {
      curl: getCurlSnippet(),
      python: getPythonSnippet(),
      javascript: getJsSnippet(),
    };
  }, [endpoint, requestBody]);

  return (
    <Card className="w-full max-w-6xl mx-auto shadow-2xl border-border font-mono">
      <CardHeader className="flex flex-col md:flex-row items-start md:items-center justify-between p-4 border-b border-border gap-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full md:w-auto">
          <Select value={endpoint} onValueChange={handleEndpointChange}>
            <SelectTrigger className="w-full sm:w-[280px] font-mono text-sm">
              <SelectValue placeholder="Select an endpoint" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="sign">POST /api/v1/sign</SelectItem>
              <SelectItem value="verify">POST /api/v1/verify</SelectItem>
            </SelectContent>
          </Select>
          <Input
            type="text"
            placeholder="Enter your API Key (optional for demo)"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full sm:w-[320px] font-mono text-sm"
          />
        </div>
        <Button onClick={handleRun} disabled={isLoading} className="bg-green-500 hover:bg-green-600 text-white w-full md:w-auto">
          {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
          Run
        </Button>
      </CardHeader>
      <CardContent className="p-4 grid md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold mb-2">Request Body</h3>
          <Textarea
            value={requestBody}
            onChange={(e) => setRequestBody(e.target.value)}
            rows={15}
            className="bg-muted rounded-md p-4 text-sm overflow-x-auto font-mono w-full"
          />
        </div>
        <div>
          <Tabs defaultValue="response" className="w-full">
            <TabsList>
              <TabsTrigger value="response">Response</TabsTrigger>
              <TabsTrigger value="curl">cURL</TabsTrigger>
              <TabsTrigger value="python">Python</TabsTrigger>
              <TabsTrigger value="javascript">JavaScript</TabsTrigger>
            </TabsList>
            <TabsContent value="response">
              <pre className="bg-muted rounded-md p-4 text-sm overflow-x-auto h-[340px]"><code>{response}</code></pre>
            </TabsContent>
            <TabsContent value="curl">
              <SyntaxHighlighter language="bash" style={vscDarkPlus} customStyle={{ height: '340px', margin: 0, padding: '1rem', background: 'hsl(var(--muted) / 0.5)' }} className="rounded-md overflow-x-auto text-sm">
                {codeSnippets.curl}
              </SyntaxHighlighter>
            </TabsContent>
            <TabsContent value="python">
              <SyntaxHighlighter language="python" style={vscDarkPlus} customStyle={{ height: '340px', margin: 0, padding: '1rem', background: 'hsl(var(--muted) / 0.5)' }} className="rounded-md overflow-x-auto text-sm">
                {codeSnippets.python}
              </SyntaxHighlighter>
            </TabsContent>
            <TabsContent value="javascript">
              <SyntaxHighlighter language="javascript" style={vscDarkPlus} customStyle={{ height: '340px', margin: 0, padding: '1rem', background: 'hsl(var(--muted) / 0.5)' }} className="rounded-md overflow-x-auto text-sm">
                {codeSnippets.javascript}
              </SyntaxHighlighter>
            </TabsContent>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  );
}
