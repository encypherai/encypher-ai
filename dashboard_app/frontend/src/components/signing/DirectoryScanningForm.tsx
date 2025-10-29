'use client';

import React, { useMemo, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useMutation } from 'react-query';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Button from '@/components/ui/Button';
import { useNotifications } from '@/lib/notifications';
import scanningService, { DirectoryScanPayload, DirectoryScanResponse, ScanOutputMode } from '@/services/scanningService';

interface DirectoryScanningFormProps {
  onComplete: (response: DirectoryScanResponse) => void;
  className?: string;
}

const defaultSchema = `{
  "document_title": "{file_stem}",
  "document_type": "article",
  "claim_generator": "Dashboard/ScanMark/1.0",
  "actions": [
    { "label": "custom.topic", "topic": "{topic}" }
  ]
}`;

export default function DirectoryScanningForm({ onComplete, className = '' }: DirectoryScanningFormProps) {
  const { addNotification } = useNotifications();
  const searchParams = useSearchParams();
  const initialDir = useMemo(() => searchParams.get('dir') || '', [searchParams]);
  const [directoryPath, setDirectoryPath] = useState(initialDir);
  const [recursive, setRecursive] = useState(true);
  const [includeExtensions, setIncludeExtensions] = useState('.txt,.md');
  const [excludePatterns, setExcludePatterns] = useState('');
  const [encoding, setEncoding] = useState('utf-8');
  const [markUnmarked, setMarkUnmarked] = useState(false);
  const [outputMode, setOutputMode] = useState<ScanOutputMode>('sidecar');
  const [schemaJson, setSchemaJson] = useState(defaultSchema);
  const [schemaError, setSchemaError] = useState<string | null>(null);

  const mutation = useMutation<DirectoryScanResponse, Error, DirectoryScanPayload>(
    (payload) => scanningService.scanDirectory(payload),
    {
      onSuccess: (response) => {
        addNotification({
          type: 'success',
          title: markUnmarked ? 'Scan & Mark Complete' : 'Scan Complete',
          message: markUnmarked
            ? `Marked ${response.marked} files; ${response.scanned} were already signed.`
            : `Scanned ${response.scanned} files; ${response.marked} marked (0 expected).`,
        });
        onComplete(response);
      },
      onError: (error) => {
        addNotification({
          type: 'error',
          title: 'Scan failed',
          message: error.message || 'An unexpected error occurred while scanning files.',
        });
      },
    }
  );

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSchemaError(null);

    if (!directoryPath.trim()) {
      setSchemaError('Directory path is required.');
      return;
    }

    let parsedSchema: Record<string, unknown> | undefined;
    if (markUnmarked && schemaJson.trim()) {
      try {
        parsedSchema = JSON.parse(schemaJson);
      } catch (err) {
        setSchemaError('Schema must be valid JSON.');
        return;
      }
    }

    const payload: DirectoryScanPayload = {
      directory_path: directoryPath.trim(),
      recursive,
      include_extensions: includeExtensions
        .split(',')
        .map((x) => x.trim())
        .filter(Boolean),
      exclude_patterns: excludePatterns
        .split(',')
        .map((x) => x.trim())
        .filter(Boolean),
      encoding: encoding.trim() || 'utf-8',
      mark_unmarked: markUnmarked,
      sign_output_mode: outputMode,
      schema: parsedSchema,
    };

    mutation.mutate(payload);
  };

  return (
    <Card title="Scan Directory" className={className}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Directory Path"
          name="directoryPath"
          placeholder="/path/to/content"
          onChange={(event) => setDirectoryPath(event.target.value)}
          value={directoryPath}
          required
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Include Extensions"
            name="includeExtensions"
            placeholder=".txt,.md"
            onChange={(event) => setIncludeExtensions(event.target.value)}
            value={includeExtensions}
            helperText="Comma separated (leave blank to include all files)."
          />

          <Input
            label="Exclude Patterns"
            name="excludePatterns"
            placeholder="**/drafts/*"
            onChange={(event) => setExcludePatterns(event.target.value)}
            value={excludePatterns}
            helperText="fnmatch patterns, comma separated."
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Encoding"
            name="encoding"
            placeholder="utf-8"
            onChange={(event) => setEncoding(event.target.value)}
            value={encoding}
          />

          <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              checked={recursive}
              onChange={(event) => setRecursive(event.target.checked)}
            />
            <span>Recurse into sub-directories</span>
          </label>

          <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              checked={markUnmarked}
              onChange={(event) => setMarkUnmarked(event.target.checked)}
            />
            <span>Mark unmarked files</span>
          </label>
        </div>

        {markUnmarked && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Select
                label="When marking, write output as"
                name="outputMode"
                onChange={(value) => setOutputMode(value as ScanOutputMode)}
                value={outputMode}
                options={[
                  { label: 'Sidecar (.signed)', value: 'sidecar' },
                  { label: 'Overwrite original', value: 'overwrite' },
                ]}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Sign Request Schema (JSON)
              </label>
              <textarea
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-mono shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100"
                rows={8}
                value={schemaJson}
                onChange={(event: React.ChangeEvent<HTMLTextAreaElement>) => setSchemaJson(event.target.value)}
                placeholder={defaultSchema}
              />
              {schemaError && (
                <p className="mt-2 text-sm text-red-600 dark:text-red-400">{schemaError}</p>
              )}
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Use {"{placeholders}"} like {"{topic}"}, {"{relative_path}"}.
              </p>
            </div>
          </>
        )}

        <div className="flex justify-end space-x-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setDirectoryPath('');
              setIncludeExtensions('.txt,.md');
              setExcludePatterns('');
              setEncoding('utf-8');
              setRecursive(true);
              setMarkUnmarked(false);
              setOutputMode('sidecar');
              setSchemaJson(defaultSchema);
              setSchemaError(null);
            }}
            disabled={mutation.isLoading}
          >
            Reset
          </Button>
          <Button type="submit" isLoading={mutation.isLoading}>
            {markUnmarked ? 'Scan & Mark' : 'Scan Directory'}
          </Button>
        </div>
      </form>
    </Card>
  );
}
