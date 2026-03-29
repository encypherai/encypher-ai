'use client';

import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@encypher/design-system';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { EncypherLoader } from '@encypher/icons';
import apiClient, { type ComplianceReadinessResponse, type ComplianceReadinessItem } from '../../lib/api';


type ComplianceItem = ComplianceReadinessItem;
type ComplianceReadiness = ComplianceReadinessResponse;

function ReadinessCircle({ score }: { score: number }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  let strokeColor = '#ef4444'; // red
  if (score >= 80) strokeColor = '#22c55e'; // green
  else if (score >= 50) strokeColor = '#f59e0b'; // amber

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" viewBox="0 0 128 128">
        <circle
          cx="64"
          cy="64"
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="10"
          className="dark:stroke-slate-700"
        />
        <circle
          cx="64"
          cy="64"
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 64 64)"
          className="transition-all duration-700"
        />
        <text
          x="64"
          y="60"
          textAnchor="middle"
          className="fill-slate-900 dark:fill-white text-2xl font-bold"
          fontSize="28"
          fontWeight="700"
        >
          {Math.round(score)}%
        </text>
        <text
          x="64"
          y="78"
          textAnchor="middle"
          className="fill-slate-500 dark:fill-slate-400"
          fontSize="11"
        >
          Readiness
        </text>
      </svg>
    </div>
  );
}

function StatusBadge({ status }: { status: ComplianceItem['status'] }) {
  const styles: Record<string, string> = {
    compliant:
      'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    action_needed:
      'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    unknown:
      'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400',
  };
  const labels: Record<string, string> = {
    compliant: 'Compliant',
    action_needed: 'Action Needed',
    unknown: 'Unknown',
  };
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status] || styles.unknown}`}
    >
      {labels[status] || status}
    </span>
  );
}

function groupByCategory(items: ComplianceItem[]): Record<string, ComplianceItem[]> {
  const groups: Record<string, ComplianceItem[]> = {};
  for (const item of items) {
    const cat = item.category;
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(item);
  }
  return groups;
}

export default function CompliancePage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;

  const { data, isLoading, error } = useQuery<ComplianceReadiness>({
    queryKey: ['compliance-readiness'],
    queryFn: () => apiClient.getComplianceReadiness(accessToken!),
    enabled: Boolean(accessToken),
    staleTime: 60_000,
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Print-only report header (hidden on screen) */}
        <div className="hidden print:block mb-8">
          <h1 className="text-2xl font-bold text-slate-900">EU AI Act Compliance Report</h1>
          <p className="text-sm text-slate-500 mt-1">
            Generated {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' })} -- Encypher AI
          </p>
          <hr className="my-4 border-slate-300" />
        </div>

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white print:hidden">
              EU AI Act Compliance
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 print:hidden">
              EU AI Act Compliance Deadline: August 2, 2026
            </p>
          </div>
          <Button
            variant="outline"
            className="print:hidden"
            onClick={() => window.print()}
          >
            Print Compliance Report
          </Button>
        </div>

        {/* Loading state */}
        {isLoading && (
          <Card>
            <CardContent className="py-12">
              <div className="flex flex-col items-center gap-3 text-sm text-muted-foreground">
                <EncypherLoader size="lg" />
                <span>Loading compliance data...</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error state */}
        {error && (
          <Card>
            <CardContent className="py-12">
              <p className="text-center text-sm text-red-600 dark:text-red-400">
                Failed to load compliance data. Please try again later.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Data loaded */}
        {data && (
          <>
            {/* Score overview */}
            <Card>
              <CardContent className="py-8">
                <div className="flex flex-col sm:flex-row items-center gap-6 sm:gap-10">
                  <ReadinessCircle score={data.readiness_score} />
                  <div className="text-center sm:text-left">
                    <p className="text-lg font-semibold text-slate-900 dark:text-white">
                      {data.compliant_count} of {data.total_count} requirements met
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                      Your organization&apos;s readiness for the EU AI Act transparency
                      and provenance requirements.
                    </p>
                    {data.readiness_score < 100 && (
                      <p className="text-sm text-amber-600 dark:text-amber-400 mt-2">
                        Complete the remaining items to achieve full compliance readiness.
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Grouped checklist */}
            {Object.entries(groupByCategory(data.items)).map(([category, items]) => (
              <div key={category}>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">
                  {category}
                </h2>
                <div className="space-y-3">
                  {items.map((item) => (
                    <Card key={item.id}>
                      <CardContent className="py-4">
                        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <StatusBadge status={item.status} />
                              <span className="font-medium text-slate-900 dark:text-white">
                                {item.label}
                              </span>
                            </div>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                              {item.description}
                            </p>
                            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                              {item.eu_ai_act_article}
                            </p>
                            {item.recommendation && (
                              <p className="text-sm text-amber-600 dark:text-amber-400 mt-1">
                                {item.recommendation}
                              </p>
                            )}
                          </div>
                          {item.status !== 'compliant' && (
                            <Link href={item.action_href} className="shrink-0">
                              <Button variant="outline" size="sm">
                                Take Action
                              </Button>
                            </Link>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
