'use client';

import React, { useMemo, useState } from 'react';
import { CheckCircleIcon, ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import DirectoryScanningForm from '@/components/signing/DirectoryScanningForm';
import { DirectoryScanResponse, ScannedFileResult } from '@/services/scanningService';

const statusIcon = (status: ScannedFileResult['status']) => {
  switch (status) {
    case 'marked':
    case 'scanned':
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    case 'error':
      return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
    default:
      return <ArrowPathIcon className="h-5 w-5 text-gray-400" />;
  }
};

export default function ScanningPage() {
  const [results, setResults] = useState<DirectoryScanResponse | null>(null);

  const summary = useMemo(() => {
    if (!results) return null;
    return [
      { label: 'Total Files', value: results.total_files },
      { label: 'Scanned', value: results.scanned },
      { label: 'Marked', value: results.marked },
      { label: 'Errors', value: results.errors },
      { label: 'Skipped', value: results.skipped },
    ];
  }, [results]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Scan Directory</h1>
        {results && (
          <Button variant="outline" onClick={() => setResults(null)} className="flex items-center gap-2">
            <ArrowPathIcon className="h-4 w-4" />
            Reset Results
          </Button>
        )}
      </div>

      <DirectoryScanningForm onComplete={setResults} />

      {results && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {summary?.map((stat) => (
              <Card key={stat.label} title={stat.label}>
                <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{stat.value}</p>
              </Card>
            ))}
          </div>

          <Card title="Scan Results">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-900/50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      Status
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      File
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      Signed Output
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      Document ID
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      Message
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {results.results.map((item, idx) => (
                    <tr key={`${item.file_path}-${idx}`}>
                      <td className="px-4 py-2 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          {statusIcon(item.status)}
                          <span className="text-sm capitalize text-gray-700 dark:text-gray-300">{item.status}</span>
                        </div>
                      </td>
                      <td className="px-4 py-2">
                        <p className="text-sm font-mono text-gray-900 dark:text-gray-100 break-all">{item.file_path}</p>
                      </td>
                      <td className="px-4 py-2">
                        {item.signed_path ? (
                          <p className="text-sm font-mono text-blue-600 dark:text-blue-300 break-all">{item.signed_path}</p>
                        ) : (
                          <p className="text-sm text-gray-500 dark:text-gray-400">—</p>
                        )}
                      </td>
                      <td className="px-4 py-2">
                        {item.document_id ? (
                          <div className="space-y-1">
                            <p className="text-sm font-mono text-gray-900 dark:text-gray-100 break-all">{item.document_id}</p>
                            {item.verification_url && (
                              <a
                                href={item.verification_url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-xs text-blue-600 hover:underline dark:text-blue-300"
                              >
                                Verify
                              </a>
                            )}
                          </div>
                        ) : (
                          <p className="text-sm text-gray-500 dark:text-gray-400">—</p>
                        )}
                      </td>
                      <td className="px-4 py-2">
                        <p className="text-sm text-gray-700 dark:text-gray-300">{item.message || '—'}</p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
