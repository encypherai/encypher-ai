'use client';

import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import { useMutation } from 'react-query';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { useNotifications } from '@/lib/notifications';
import demoService, { DemoGeneratePayload, DemoGenerateResponse } from '@/services/demoService';

export default function DemoPage() {
  const { addNotification } = useNotifications();

  const [basePath, setBasePath] = useState('demo_corpus');
  const [topicsCsv, setTopicsCsv] = useState('politics,sports,tech,finance,health');
  const [filesPerTopic, setFilesPerTopic] = useState('20');
  const [paragraphsPerFile, setParagraphsPerFile] = useState('3');
  const [overwrite, setOverwrite] = useState(false);
  const [seed, setSeed] = useState('');

  const [result, setResult] = useState<DemoGenerateResponse | null>(null);

  const mutation = useMutation<DemoGenerateResponse, Error, DemoGeneratePayload>(
    (payload) => demoService.generate(payload),
    {
      onSuccess: (data) => {
        setResult(data);
        addNotification({
          type: 'success',
          title: 'Demo corpus ready',
          message: `Created ${data.total_files} files across ${data.topics_created.length} topics.`,
        });
      },
      onError: (error) => {
        addNotification({
          type: 'error',
          title: 'Demo generation failed',
          message: error.message || 'An unexpected error occurred while generating demo data.',
        });
      },
    }
  );

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setResult(null);

    const payload: DemoGeneratePayload = {
      base_path: basePath.trim() || 'demo_corpus',
      overwrite,
      files_per_topic: Math.max(1, Math.min(1000, parseInt(filesPerTopic || '20', 10))),
      paragraphs_per_file: Math.max(1, Math.min(20, parseInt(paragraphsPerFile || '3', 10))),
    };

    const topicsArr = topicsCsv
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);
    if (topicsArr.length) payload.topics = topicsArr;

    if (seed.trim()) {
      const seedNum = Number(seed);
      if (!Number.isNaN(seedNum)) payload.seed = seedNum;
    }

    mutation.mutate(payload);
  };

  const quickLinks = useMemo(() => {
    if (!result) return null;
    const dir = encodeURIComponent(result.base_path);
    return (
      <div className="flex flex-wrap gap-3">
        <Link href={`/dashboard/signing?dir=${dir}`} className="btn btn-primary px-3 py-2 rounded-md text-white bg-primary-600 hover:bg-primary-700">
          Open Signing for this corpus
        </Link>
        <Link href={`/dashboard/signing/scan?dir=${dir}`} className="btn btn-outline px-3 py-2 rounded-md border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200">
          Open Scanning for this corpus
        </Link>
      </div>
    );
  }, [result]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Demo Data Generator</h1>

      <Card title="Generate Sample Corpus">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Base Path"
            name="basePath"
            placeholder="demo_corpus or C:\\path\\to\\demo"
            value={basePath}
            onChange={(e) => setBasePath(e.target.value)}
            required
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Topics (comma separated)"
              name="topics"
              placeholder="politics,sports,tech"
              value={topicsCsv}
              onChange={(e) => setTopicsCsv(e.target.value)}
            />
            <Input
              label="Files per Topic"
              name="filesPerTopic"
              type="number"
              min={1}
              max={1000}
              value={filesPerTopic}
              onChange={(e) => setFilesPerTopic(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Paragraphs per File"
              name="paragraphsPerFile"
              type="number"
              min={1}
              max={20}
              value={paragraphsPerFile}
              onChange={(e) => setParagraphsPerFile(e.target.value)}
            />

            <Input
              label="Random Seed (optional)"
              name="seed"
              placeholder="e.g. 42"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
            />

            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 dark:text-gray-300 mt-6">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                checked={overwrite}
                onChange={(e) => setOverwrite(e.target.checked)}
              />
              <span>Overwrite if directory exists</span>
            </label>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setBasePath('demo_corpus');
                setTopicsCsv('politics,sports,tech,finance,health');
                setFilesPerTopic('20');
                setParagraphsPerFile('3');
                setOverwrite(false);
                setSeed('');
                setResult(null);
              }}
              disabled={mutation.isLoading}
            >
              Reset
            </Button>
            <Button type="submit" isLoading={mutation.isLoading}>Generate</Button>
          </div>
        </form>
      </Card>

      {result && (
        <Card title="Demo Corpus Created">
          <div className="space-y-2">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <strong>Base Path:</strong> <span className="font-mono">{result.base_path}</span>
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <strong>Topics:</strong> {result.topics_created.join(', ')}
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <strong>Total Files:</strong> {result.total_files} ({result.files_per_topic} per topic)
            </p>
            {quickLinks}
          </div>
        </Card>
      )}
    </div>
  );
}
