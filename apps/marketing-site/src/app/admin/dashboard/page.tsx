'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Users,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  PieChart,
  BarChart,
  RefreshCw,
  ArrowRight,
  ArrowUpRight,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';

// UI Components
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/use-toast';

// API
import { getInvestorAccessStats, getInvestorAccessRecords, InvestorAccessRecord } from '@/lib/admin-api';

export default function AdminDashboardPage() {
  const { data: session, status: sessionStatus } = useSession();
  const router = useRouter();
  const { toast } = useToast();
  
  // State
  const [loading, setLoading] = useState<boolean>(true);
  const [stats, setStats] = useState<{
    total: number;
    pending: number;
    active: number;
    rejected: number;
    revoked: number;
    expired: number;
  }>({
    total: 0,
    pending: 0,
    active: 0,
    rejected: 0,
    revoked: 0,
    expired: 0,
  });
  const [recentRequests, setRecentRequests] = useState<InvestorAccessRecord[]>([]);
  
  // Fetch dashboard stats
  const fetchDashboardStats = useCallback(async () => {
    if (sessionStatus !== 'authenticated' || !session?.accessToken) return;
    
    setLoading(true);
    try {
      // Fetch stats
      const statsData = await getInvestorAccessStats(session.accessToken);
      setStats(statsData);
      
      // Fetch recent requests
      const recentData = await getInvestorAccessRecords(
        session.accessToken,
        1,
        5,
        '' // No status filter to get all recent requests
      );
      setRecentRequests(recentData.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      toast({
        title: 'Error',
        description: 'Failed to load dashboard statistics. Please try again.',
        variant: 'error',
      });
    } finally {
      setLoading(false);
    }
  }, [session, sessionStatus, toast]);
  
  // Effect to fetch data when dependencies change
  useEffect(() => {
    if (sessionStatus === 'authenticated') {
      fetchDashboardStats();
    }
  }, [sessionStatus, fetchDashboardStats]);
  
  // Redirect if not authenticated
  if (sessionStatus === 'unauthenticated') {
    router.push('/auth/signin?callbackUrl=/admin/dashboard');
    return null;
  }
  
  // Calculate approval rate
  const approvalRate = stats.total > 0
    ? Math.round((stats.active / stats.total) * 100)
    : 0;
  
  // Calculate rejection rate
  const rejectionRate = stats.total > 0
    ? Math.round((stats.rejected / stats.total) * 100)
    : 0;
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Overview of investor access requests and statistics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchDashboardStats()}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>
      
      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">{stats.total}</div>
            )}
            <p className="text-xs text-muted-foreground">
              All investor access requests
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approval</CardTitle>
            <Clock className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold text-amber-500">{stats.pending}</div>
            )}
            <p className="text-xs text-muted-foreground">
              Requests awaiting admin approval
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Investors</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold text-green-500">{stats.active}</div>
            )}
            <p className="text-xs text-muted-foreground">
              Approved investor access requests
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejected Requests</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold text-red-500">{stats.rejected}</div>
            )}
            <p className="text-xs text-muted-foreground">
              Rejected investor access requests
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approval Rate</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {approvalRate}%
                {approvalRate > 50 ? (
                  <TrendingUp className="h-4 w-4 text-green-500 inline ml-2" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500 inline ml-2" />
                )}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              Percentage of approved requests
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejection Rate</CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {rejectionRate}%
                {rejectionRate > 50 ? (
                  <TrendingUp className="h-4 w-4 text-red-500 inline ml-2" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-green-500 inline ml-2" />
                )}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              Percentage of rejected requests
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Other Statuses</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {stats.revoked + stats.expired}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              Revoked or expired access requests
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Recent Requests */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Investor Requests</CardTitle>
            <Button variant="outline" size="sm" asChild>
              <Link href="/admin/investor-requests">
                View All
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
          <CardDescription>
            The most recent investor access requests
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, index) => (
                <div key={`skeleton-${index}`} className="flex items-center justify-between py-2">
                  <div className="space-y-1">
                    <Skeleton className="h-4 w-40" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                  <Skeleton className="h-8 w-24 rounded-md" />
                </div>
              ))}
            </div>
          ) : recentRequests.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <AlertTriangle className="h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-muted-foreground">No investor requests found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {recentRequests.map((request) => (
                <div key={request.id} className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-4 last:border-0 last:pb-0">
                  <div>
                    <div className="font-medium">{request.investor_name || request.investor_email}</div>
                    <div className="text-sm text-muted-foreground">{request.investor_company || 'No company'}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    {request.status === 'PENDING_APPROVAL' ? (
                      <Button variant="outline" size="sm" asChild>
                        <Link href={`/admin/investor-requests/${request.id}`}>
                          Review
                        </Link>
                      </Button>
                    ) : (
                      <div className="flex items-center gap-1 text-sm">
                        {request.status === 'ACTIVE' && (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        )}
                        {request.status === 'REJECTED' && (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        {request.status}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
        <CardFooter className="border-t border-gray-200 dark:border-gray-700 px-6 py-4">
          <Button variant="outline" className="w-full" asChild>
            <Link href="/admin/investor-requests">
              View All Investor Requests
              <ArrowUpRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
