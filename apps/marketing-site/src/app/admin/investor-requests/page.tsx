'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

// Import our custom admin API hook
import { useAdminApi, InvestorAccessRecord } from '@/lib/hooks/useAdminApi';

// Icons
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  MoreHorizontal,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Search,
  Download,
} from 'lucide-react';
import { format } from 'date-fns';

// UI Components
import { Card, CardContent, CardHeader, CardTitle } from '@encypher/design-system';
import { Button } from '@encypher/design-system';
import { Input } from '@encypher/design-system';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@encypher/design-system';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@encypher/design-system';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@encypher/design-system';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@encypher/design-system';
import { Badge } from '@encypher/design-system';

import { Skeleton } from '@encypher/design-system';
import { useToast } from '@encypher/design-system';

// Utils
import { exportInvestorRecordsToCSV } from '@/lib/export-utils';

// Custom Hook: useDebounce (Consider moving to a shared hooks file)
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

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
          <AlertCircle className="h-3 w-3 mr-1" />
          Revoked
        </Badge>
      );
    case 'EXPIRED':
      return (
        <Badge variant="outline" className="bg-gray-50 text-gray-700 border-gray-200">
          <AlertCircle className="h-3 w-3 mr-1" />
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

export default function InvestorRequestsPage() {
  const router = useRouter();

  // Use our custom admin API hook
  const {
    getInvestorAccessRecords,
    approveInvestorAccess,
    rejectInvestorAccess,
    isAuthenticated
  } = useAdminApi();

  // State
  const [investors, setInvestors] = useState<InvestorAccessRecord[]>([]);
  const [totalInvestors, setTotalInvestors] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const debouncedSearchQuery = useDebounce(searchQuery, 500); // Debounce search query
  const [exporting, setExporting] = useState<boolean>(false);
  const [selectedInvestor, setSelectedInvestor] = useState<InvestorAccessRecord | null>(null);
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);
  const [actionDialogOpen, setActionDialogOpen] = useState<boolean>(false);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const { toast } = useToast();
  const [fetchFailCount, setFetchFailCount] = useState<number>(0);
  const MAX_FETCH_ATTEMPTS = 2;

  useEffect(() => {
    console.log('[InvestorRequests] Filters (statusFilter or debouncedSearchQuery) changed, resetting fetch fail count.');
    setFetchFailCount(0);
  }, [statusFilter, debouncedSearchQuery]); // Depend on debouncedSearchQuery

  // Fetch investor records
  const fetchInvestors = useCallback(async () => {
    if (!isAuthenticated) {
      console.log('[InvestorRequests] Not authenticated, skipping fetch');
      return;
    }

    if (fetchFailCount >= MAX_FETCH_ATTEMPTS) {
      console.warn(`[InvestorRequests] Max fetch attempts (${MAX_FETCH_ATTEMPTS}) reached for current filters. Further automatic fetching paused.`);
      setLoading(false);
      return;
    }

    setLoading(true);

    try {
      const filterStatus = statusFilter !== 'ALL' ? statusFilter : undefined;

      // Pass debouncedSearchQuery to the API call
      const response = await getInvestorAccessRecords(currentPage, pageSize, filterStatus, debouncedSearchQuery);
      setInvestors(response.data);
      setTotalInvestors(response.total);
      setTotalPages(Math.ceil(response.total / pageSize));
      setFetchFailCount(0); // Reset fail count on success
    } catch (err) {
      console.error('[InvestorRequests] Error fetching investors:', err);
      const newFailCount = fetchFailCount + 1;
      setFetchFailCount(newFailCount);

      let description = err instanceof Error ? err.message : 'Failed to fetch investor records';
      if (newFailCount >= MAX_FETCH_ATTEMPTS) {
        description += ' Further automatic fetching is paused for the current view. Please change filters or refresh.';
      }
      toast({
        title: 'Error Fetching Records',
        description: description,
        variant: "error"
      });
    } finally {
      setLoading(false);
    }
  }, [
    isAuthenticated,
    statusFilter,
    currentPage,
    pageSize,
    getInvestorAccessRecords, // This is now stable from useAdminApi
    toast,
    fetchFailCount,
    debouncedSearchQuery // Add debouncedSearchQuery as a dependency
  ]);

  // Effect to trigger fetching investors when relevant dependencies change
  useEffect(() => {
    fetchInvestors();
  }, [fetchInvestors]); // This is the critical part

  // Export all investor records
  const handleExport = async () => {
    if (!isAuthenticated) {
      toast({
        title: 'Authentication Required',
        description: 'Please sign in to export investor records.',
      });
      return;
    }

    setExporting(true);

    try {
      // Fetch all records (with a larger limit)
      const response = await getInvestorAccessRecords(1, 1000);

      // Export to CSV
      exportInvestorRecordsToCSV(response.data);

      toast({
        title: 'Export Successful',
        description: `Exported ${response.data.length} investor records.`,
      });
    } catch (err) {
      console.error('Export error:', err);
      toast({
        title: 'Export Failed',
        description: err instanceof Error ? err.message : 'Failed to export investor records',
      });
    } finally {
      setExporting(false);
    }
  };

  // Handle approve/reject actions
  const handleAction = async () => {
    if (!selectedInvestor || !actionType) {
      return;
    }

    setActionLoading(true);

    try {
      let result;
      if (actionType === 'approve') {
        result = await approveInvestorAccess(selectedInvestor.id);
      } else {
        result = await rejectInvestorAccess(selectedInvestor.id);
      }

      if (result.success) {
        toast({
          title: `${actionType === 'approve' ? 'Approved' : 'Rejected'} Successfully`,
          description: result.message,
        });
        fetchInvestors(); // Refresh the list
      } else {
        throw new Error(result.message);
      }
    } catch (err) {
      console.error(`${actionType} error:`, err);
      toast({
        title: `${actionType === 'approve' ? 'Approval' : 'Rejection'} Failed`,
        description: err instanceof Error ? err.message : `Failed to ${actionType} investor access`,
      });
    } finally {
      setActionLoading(false);
      setActionDialogOpen(false);
      setSelectedInvestor(null);
      setActionType(null);
    }
  };

  // Handle status filter change
  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value);
    setCurrentPage(1); // Reset to first page when filter changes
  };

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Implement search functionality
    // This would typically involve adding a search parameter to the API call
    // For now, we'll just log it
    console.log('Searching for:', searchQuery);
  };

  // Calculate pagination
  const startRecord = (currentPage - 1) * pageSize + 1;
  const endRecord = Math.min(currentPage * pageSize, totalInvestors);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/signin?callbackUrl=/admin/investor-requests');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Investor Requests</h1>
          <p className="text-muted-foreground mt-1">
            Manage and review investor access requests
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchInvestors()}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={handleExport}
            disabled={exporting}
          >
            {exporting ? (
              <Download className={`h-4 w-4 mr-2 animate-spin`} />
            ) : (
              <Download className={`h-4 w-4 mr-2`} />
            )}
            Export
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-white dark:bg-gray-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalInvestors}</div>
          </CardContent>
        </Card>
        <Card className="bg-white dark:bg-gray-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending Approval</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-600">
              {investors.filter((i) => i.status === 'PENDING_APPROVAL').length}
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white dark:bg-gray-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {investors.filter((i) => i.status === 'ACTIVE').length}
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white dark:bg-gray-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Rejected</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {investors.filter((i) => i.status === 'REJECTED').length}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 flex flex-col md:flex-row gap-4 justify-between">
          <div className="flex flex-col sm:flex-row gap-2">
            <Select
              value={statusFilter}
              onValueChange={handleStatusFilterChange}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Statuses</SelectItem>
                <SelectItem value="PENDING_APPROVAL">Pending Approval</SelectItem>
                <SelectItem value="ACTIVE">Active</SelectItem>
                <SelectItem value="REJECTED">Rejected</SelectItem>
                <SelectItem value="REVOKED">Revoked</SelectItem>
                <SelectItem value="EXPIRED">Expired</SelectItem>
                <SelectItem value="PENDING_VERIFICATION">Pending Verification</SelectItem>
              </SelectContent>
            </Select>
            <form onSubmit={handleSearch} className="flex gap-2">
              <Input
                placeholder="Search by email or name"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full sm:w-[300px]"
              />
              <Button type="submit" variant="outline" size="icon">
                <Search className="h-4 w-4" />
              </Button>
            </form>
          </div>
          <div className="flex items-center gap-2">
            <Select
              value={pageSize.toString()}
              onValueChange={(value) => console.log(`Page size change to ${value} is not implemented`)}
            >
              <SelectTrigger className="w-[80px]">
                <SelectValue placeholder="10" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="20">20</SelectItem>
                <SelectItem value="50">50</SelectItem>
              </SelectContent>
            </Select>
            <span className="text-sm text-muted-foreground">
              Showing {startRecord}-{endRecord} of {totalInvestors}
            </span>
          </div>
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700">
          <div className="relative overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Investor</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Company</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Last Updated</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  // Loading skeletons
                  Array.from({ length: pageSize }).map((_, index) => (
                    <TableRow key={`skeleton-${index}`}>
                      <TableCell><Skeleton className="h-5 w-32" /></TableCell>
                      <TableCell><Skeleton className="h-5 w-40" /></TableCell>
                      <TableCell><Skeleton className="h-5 w-32" /></TableCell>
                      <TableCell><Skeleton className="h-5 w-28" /></TableCell>
                      <TableCell><Skeleton className="h-5 w-28" /></TableCell>
                      <TableCell><Skeleton className="h-5 w-28" /></TableCell>
                      <TableCell className="text-right"><Skeleton className="h-8 w-8 rounded-full ml-auto" /></TableCell>
                    </TableRow>
                  ))
                ) : investors.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8">
                      <div className="flex flex-col items-center justify-center">
                        <AlertCircle className="h-8 w-8 text-muted-foreground mb-2" />
                        <p className="text-muted-foreground">No investor requests found</p>
                        {statusFilter && (
                          <Button
                            variant="link"
                            onClick={() => setStatusFilter('ALL')}
                            className="mt-2"
                          >
                            Clear filters
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  investors.map((investor) => (
                    <TableRow key={investor.id}>
                      <TableCell className="font-medium">
                        {investor.investor_name || 'N/A'}
                      </TableCell>
                      <TableCell>{investor.investor_email}</TableCell>
                      <TableCell>{investor.investor_company || 'N/A'}</TableCell>
                      <TableCell>
                        <StatusBadge status={investor.status} />
                      </TableCell>
                      <TableCell>
                        {investor.created_at
                          ? format(new Date(investor.created_at), 'MMM d, yyyy')
                          : 'N/A'}
                      </TableCell>
                      <TableCell>
                        {investor.updated_at
                          ? format(new Date(investor.updated_at), 'MMM d, yyyy')
                          : 'N/A'}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                              <span className="sr-only">Open menu</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            {investor.status === 'PENDING_APPROVAL' && (
                              <>
                                <DropdownMenuItem
                                  onClick={() => {
                                    setSelectedInvestor(investor);
                                    setActionType('approve');
                                    setActionDialogOpen(true);
                                  }}
                                >
                                  <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                                  Approve
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={() => {
                                    setSelectedInvestor(investor);
                                    setActionType('reject');
                                    setActionDialogOpen(true);
                                  }}
                                >
                                  <XCircle className="h-4 w-4 mr-2 text-red-600" />
                                  Reject
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                              </>
                            )}
                            <DropdownMenuItem>View Details</DropdownMenuItem>
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-4 border-t border-gray-200 dark:border-gray-700">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1 || loading}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>
            <div className="text-sm text-muted-foreground">
              Page {currentPage} of {totalPages}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages || loading}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        )}
      </div>

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
                <span className="text-muted-foreground">Name:</span>{' '}
                {selectedInvestor?.investor_name || 'N/A'}
              </li>
              <li className="text-sm">
                <span className="text-muted-foreground">Email:</span>{' '}
                {selectedInvestor?.investor_email}
              </li>
              <li className="text-sm">
                <span className="text-muted-foreground">Company:</span>{' '}
                {selectedInvestor?.investor_company || 'N/A'}
              </li>
            </ul>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setActionDialogOpen(false);
                setSelectedInvestor(null);
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
