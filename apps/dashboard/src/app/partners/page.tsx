'use client';

import React from 'react';
import {
  Badge,
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@encypher/design-system';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import apiClient from '../../lib/api';

function StatCardSkeleton() {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="h-4 w-24 bg-muted rounded animate-pulse mb-2" />
        <div className="h-8 w-20 bg-muted rounded animate-pulse mb-1" />
      </CardContent>
    </Card>
  );
}

function TableSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="h-12 bg-muted rounded animate-pulse" />
      ))}
    </div>
  );
}

function formatDate(iso: string | null): string {
  if (!iso) return '--';
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export default function PartnersPage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;

  const {
    data: aggregate,
    isLoading: aggLoading,
  } = useQuery({
    queryKey: ['partner-aggregate'],
    queryFn: () => apiClient.getPartnerAggregate(accessToken!),
    enabled: Boolean(accessToken),
    staleTime: 30_000,
  });

  const {
    data: publishersData,
    isLoading: pubLoading,
  } = useQuery({
    queryKey: ['partner-publishers'],
    queryFn: () => apiClient.getPartnerPublishers(accessToken!),
    enabled: Boolean(accessToken),
    staleTime: 30_000,
  });

  const publishers = publishersData?.publishers ?? [];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Partner Portal</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Manage your child publisher organizations and view aggregate stats.
            </p>
          </div>
          <Link href="/api-keys">
            <Button variant="primary">Onboard Publishers</Button>
          </Link>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {aggLoading ? (
            <>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : (
            <>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">Total Publishers</p>
                  <p className="text-2xl font-bold">{aggregate?.total_publishers ?? 0}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">Documents Signed</p>
                  <p className="text-2xl font-bold">{aggregate?.total_documents_signed ?? 0}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">Verifications</p>
                  <p className="text-2xl font-bold">{aggregate?.total_verifications ?? 0}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">Spread Detections</p>
                  <p className="text-2xl font-bold">{aggregate?.total_spread_detections ?? 0}</p>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Publishers table */}
        <Card>
          <CardHeader>
            <CardTitle>Publishers</CardTitle>
            <CardDescription>
              Child publisher organizations provisioned under your partner account.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {pubLoading ? (
              <TableSkeleton />
            ) : publishers.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <p className="text-lg font-medium">No publishers yet</p>
                <p className="text-sm mt-1">
                  Use the bulk provisioning API or the Onboard Publishers button to get started.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-muted-foreground">
                      <th className="pb-3 font-medium">Name</th>
                      <th className="pb-3 font-medium">Tier</th>
                      <th className="pb-3 font-medium">Coalition</th>
                      <th className="pb-3 font-medium">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {publishers.map((pub: any) => (
                      <tr key={pub.id} className="border-b last:border-0">
                        <td className="py-3 font-medium text-foreground">{pub.name}</td>
                        <td className="py-3">
                          <Badge variant="secondary">{pub.tier}</Badge>
                        </td>
                        <td className="py-3">
                          {pub.coalition_member ? (
                            <Badge variant="default">Yes</Badge>
                          ) : (
                            <span className="text-muted-foreground">No</span>
                          )}
                        </td>
                        <td className="py-3 text-muted-foreground">{formatDate(pub.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
