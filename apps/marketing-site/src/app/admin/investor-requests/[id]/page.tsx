'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { format } from 'date-fns';
import {
  CheckCircle,
  XCircle,
  Clock,
  ArrowLeft,
  RefreshCw,
  Mail,
  Building,
  Calendar,
  Eye,
  Activity,
  AlertTriangle,
  Edit,
} from 'lucide-react';

// UI Components
import { Button } from '@encypher/design-system';
import { Card, CardContent, CardHeader, CardTitle } from '@encypher/design-system';
import { Badge } from '@encypher/design-system';
import { Skeleton } from '@encypher/design-system';
import { useToast } from '@encypher/design-system';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@encypher/design-system';

// API
import {
  getInvestorAccessById,
  approveInvestorAccess,
  rejectInvestorAccess,
  InvestorAccessRecord,
} from '@/lib/admin-api';

// Status badge component
const StatusBadge = ({ status }: { status: string }) => {
  switch (status) {
    case 'PENDING_APPROVAL':
      return (
        <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200">
          <Clock className="h-3 w-3 mr-1" />
          Pending Approval
        </Badge>
      );
    case 'ACTIVE':
      return (
        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
          <CheckCircle className="h-3 w-3 mr-1" />
          Active
        </Badge>
      );
    case 'REJECTED':
      return (
        <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
          <XCircle className="h-3 w-3 mr-1" />
          Rejected
        </Badge>
      );
    case 'REVOKED':
      return (
        <Badge variant="outline" className="bg-gray-50 text-gray-700 border-gray-200">
          <AlertTriangle className="h-3 w-3 mr-1" />
          Revoked
        </Badge>
      );
    case 'EXPIRED':
      return (
        <Badge variant="outline" className="bg-gray-50 text-gray-700 border-gray-200">
          <AlertTriangle className="h-3 w-3 mr-1" />
          Expired
        </Badge>
      );
    case 'PENDING_VERIFICATION':
      return (
        <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
          <Clock className="h-3 w-3 mr-1" />
          Pending Verification
        </Badge>
      );
    default:
      return (
        <Badge variant="outline" className="bg-gray-50 text-gray-700 border-gray-200">
          {status}
        </Badge>
      );
  }
};

export default function InvestorRequestDetailPage() {
  const { data: session, status: sessionStatus } = useSession();
  const router = useRouter();
  const params = useParams();
  const investorId = params.id as string;

  // State
  const [investor, setInvestor] = useState<InvestorAccessRecord | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionDialogOpen, setActionDialogOpen] = useState<boolean>(false);
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const { toast } = useToast();

  // Fetch investor details
  const fetchInvestorDetails = useCallback(async () => {
    if (sessionStatus !== 'authenticated' || !session?.accessToken) return;

    setLoading(true);
    try {
      const data = await getInvestorAccessById(session.accessToken, investorId);
      setInvestor(data);
    } catch (error) {
      console.error('Error fetching investor details:', error);
      toast({
        title: 'Error',
        description: 'Failed to load investor details. Please try again.',
        variant: 'error',
      });
    } finally {
      setLoading(false);
    }
  }, [session, sessionStatus, investorId, toast]);

  // Handle approve/reject actions
  const handleAction = async () => {
    if (!investor || !actionType || !session?.accessToken) return;

    setActionLoading(true);
    try {
      if (actionType === 'approve') {
        await approveInvestorAccess(session.accessToken, investor.id);
        toast({
          title: 'Success',
          description: `Investor access for ${investor.investor_email} has been approved.`,
        });
      } else {
        await rejectInvestorAccess(session.accessToken, investor.id);
        toast({
          title: 'Success',
          description: `Investor access for ${investor.investor_email} has been rejected.`,
        });
      }

      // Refresh the details
      fetchInvestorDetails();
    } catch (error) {
      console.error(`Error ${actionType}ing investor access:`, error);
      toast({
        title: 'Error',
        description: `Failed to ${actionType} investor access. Please try again.`,
        variant: 'error',
      });
    } finally {
      setActionLoading(false);
      setActionDialogOpen(false);
      setActionType(null);
    }
  };

  // Effect to fetch data when dependencies change
  useEffect(() => {
    if (sessionStatus === 'authenticated' && investorId) {
      fetchInvestorDetails();
    }
  }, [sessionStatus, investorId, fetchInvestorDetails]);

  // Redirect if not authenticated
  if (sessionStatus === 'unauthenticated') {
    router.push('/auth/signin?callbackUrl=/admin/investor-requests');
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            asChild
            className="h-8 gap-1"
          >
            <Link href="/admin/investor-requests">
              <ArrowLeft className="h-4 w-4" />
              Back
            </Link>
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">Investor Request Details</h1>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchInvestorDetails}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          {investor?.status === 'PENDING_APPROVAL' && (
            <>
              <Button
                variant="default"
                size="sm"
                onClick={() => {
                  setActionType('approve');
                  setActionDialogOpen(true);
                }}
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => {
                  setActionType('reject');
                  setActionDialogOpen(true);
                }}
              >
                <XCircle className="h-4 w-4 mr-2" />
                Reject
              </Button>
            </>
          )}
        </div>
      </div>

      {loading ? (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <Skeleton className="h-5 w-32" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Skeleton className="h-5 w-32" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </CardContent>
          </Card>
        </div>
      ) : investor ? (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Investor Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-2">
                <Mail className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="font-medium">{investor.investor_email}</p>
                  <p className="text-sm text-muted-foreground">Email Address</p>
                </div>
              </div>

              <div className="flex items-start gap-2">
                <Building className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="font-medium">{investor.investor_company || 'Not specified'}</p>
                  <p className="text-sm text-muted-foreground">Company</p>
                </div>
              </div>

              <div className="flex items-start gap-2">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="font-medium">
                    {investor.created_at
                      ? format(new Date(investor.created_at), 'MMMM d, yyyy')
                      : 'N/A'}
                  </p>
                  <p className="text-sm text-muted-foreground">Request Date</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Access Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-2">
                <Activity className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <div className="mb-1">
                    <StatusBadge status={investor.status} />
                  </div>
                  <p className="text-sm text-muted-foreground">Current Status</p>
                </div>
              </div>

              <div className="flex items-start gap-2">
                <Eye className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="font-medium">{investor.visit_count || 0}</p>
                  <p className="text-sm text-muted-foreground">Visit Count</p>
                </div>
              </div>

              <div className="flex items-start gap-2">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="font-medium">
                    {investor.last_visited_at
                      ? format(new Date(investor.last_visited_at), 'MMMM d, yyyy')
                      : 'Never'}
                  </p>
                  <p className="text-sm text-muted-foreground">Last Visited</p>
                </div>
              </div>

              {investor.email_verified_at && (
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium">
                      {format(new Date(investor.email_verified_at), 'MMMM d, yyyy')}
                    </p>
                    <p className="text-sm text-muted-foreground">Email Verified</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-xl">Activity Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative pl-6 border-l border-gray-200 dark:border-gray-700 space-y-6">
                <div className="relative">
                  <div className="absolute -left-9 mt-1.5 h-4 w-4 rounded-full bg-primary"></div>
                  <div className="mb-1 text-sm font-semibold">
                    Request Created
                  </div>
                  <time className="text-xs text-muted-foreground">
                    {investor.created_at
                      ? format(new Date(investor.created_at), 'MMMM d, yyyy h:mm a')
                      : 'N/A'}
                  </time>
                  <p className="mt-2 text-sm">
                    Investor {investor.investor_name || investor.investor_email} requested access to the pitch deck.
                  </p>
                </div>

                {investor.status !== 'PENDING_APPROVAL' && (
                  <div className="relative">
                    <div className={`absolute -left-9 mt-1.5 h-4 w-4 rounded-full ${
                      investor.status === 'ACTIVE' ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <div className="mb-1 text-sm font-semibold">
                      {investor.status === 'ACTIVE' ? 'Request Approved' : 'Request Rejected'}
                    </div>
                    <time className="text-xs text-muted-foreground">
                      {investor.updated_at
                        ? format(new Date(investor.updated_at), 'MMMM d, yyyy h:mm a')
                        : 'N/A'}
                    </time>
                    <p className="mt-2 text-sm">
                      {investor.status === 'ACTIVE'
                        ? 'Admin approved the investor access request.'
                        : 'Admin rejected the investor access request.'}
                    </p>
                  </div>
                )}

                {investor.email_verified_at && (
                  <div className="relative">
                    <div className="absolute -left-9 mt-1.5 h-4 w-4 rounded-full bg-blue-500"></div>
                    <div className="mb-1 text-sm font-semibold">
                      Email Verified
                    </div>
                    <time className="text-xs text-muted-foreground">
                      {format(new Date(investor.email_verified_at), 'MMMM d, yyyy h:mm a')}
                    </time>
                    <p className="mt-2 text-sm">
                      Investor verified their email address.
                    </p>
                  </div>
                )}

                {investor.last_visited_at && (
                  <div className="relative">
                    <div className="absolute -left-9 mt-1.5 h-4 w-4 rounded-full bg-purple-500"></div>
                    <div className="mb-1 text-sm font-semibold">
                      Last Visited
                    </div>
                    <time className="text-xs text-muted-foreground">
                      {format(new Date(investor.last_visited_at), 'MMMM d, yyyy h:mm a')}
                    </time>
                    <p className="mt-2 text-sm">
                      Investor last accessed the pitch deck.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-amber-500 mb-4" />
            <h2 className="text-xl font-semibold mb-2">Investor Not Found</h2>
            <p className="text-muted-foreground text-center mb-6">
              The investor request you're looking for doesn't exist or you don't have permission to view it.
            </p>
            <Button asChild>
              <Link href="/admin/investor-requests">
                Return to Investor Requests
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Approve/Reject Dialog */}
      <Dialog open={actionDialogOpen} onOpenChange={setActionDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {actionType === 'approve' ? 'Approve Investor Access' : 'Reject Investor Access'}
            </DialogTitle>
            <DialogDescription>
              {actionType === 'approve'
                ? 'This will grant the investor access to the pitch deck.'
                : 'This will reject the investor access request.'}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm font-medium">Investor Details:</p>
            <ul className="mt-2 space-y-1">
              <li className="text-sm">
                <span className="text-muted-foreground">Name:</span>{" "}
                {investor?.investor_name || "N/A"}
              </li>
              <li className="text-sm">
                <span className="text-muted-foreground">Email:</span>{" "}
                {investor?.investor_email}
              </li>
              <li className="text-sm">
                <span className="text-muted-foreground">Company:</span>{" "}
                {investor?.investor_company || "N/A"}
              </li>
            </ul>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setActionDialogOpen(false);
                setActionType(null);
              }}
              disabled={actionLoading}
            >
              Cancel
            </Button>
            <Button
              variant={actionType === 'approve' ? 'default' : 'destructive'}
              onClick={handleAction}
              disabled={actionLoading}
            >
              {actionLoading && <RefreshCw className="h-4 w-4 mr-2 animate-spin" />}
              {actionType === 'approve' ? 'Approve' : 'Reject'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
