# PRD-004: Dashboard Coalition Features

**Status**: Draft  
**Priority**: P1 (High)  
**Estimated Effort**: 2-3 weeks  
**Owner**: Frontend Team  
**Created**: 2025-11-04  
**Depends On**: PRD-001 (Coalition Infrastructure)

---

## Executive Summary

Add coalition features to the dashboard app (/dashboard_app), including coalition stats, revenue tracking, content analytics, and membership management for both coalition members and administrators.

---

## Problem Statement

### Current State
- Dashboard only shows signing/verification stats
- No coalition visibility for free tier users
- No admin tools for coalition management
- Missing revenue tracking UI

### Desired State
- Coalition tab with comprehensive stats
- Revenue tracking dashboard for members
- Admin panel for coalition management
- Content analytics showing AI company interest

---

## User Stories

### Story 1: Coalition Member - View Stats
**As a** coalition member  
**I want to** see my coalition statistics and revenue  
**So that** I understand my contribution and earnings

**Acceptance Criteria:**
- [ ] Coalition tab in main navigation
- [ ] Stats cards: documents, verifications, revenue
- [ ] Revenue breakdown by period
- [ ] Content access logs

### Story 2: Admin - Manage Coalition
**As an** Encypher admin  
**I want to** manage coalition members and agreements  
**So that** I can oversee the coalition operations

**Acceptance Criteria:**
- [ ] Admin-only coalition management page
- [ ] Member list with stats
- [ ] Agreement management interface
- [ ] Revenue distribution controls

---

## UI Components

### Coalition Dashboard (Member View)

```typescript
// frontend/app/coalition/page.tsx

export default function CoalitionPage() {
  const { data: stats } = useCoalitionStats();
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Coalition Dashboard</h1>
      
      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Signed Documents"
          value={stats?.content_stats.total_documents}
          icon={<FileText />}
          trend="+12% this month"
        />
        <StatCard
          title="Verifications"
          value={stats?.content_stats.verification_count}
          icon={<CheckCircle />}
          trend="+8% this month"
        />
        <StatCard
          title="Total Earned"
          value={`$${stats?.revenue_stats.total_earned.toFixed(2)}`}
          icon={<DollarSign />}
          trend="+$125 this month"
        />
        <StatCard
          title="Pending Payout"
          value={`$${stats?.revenue_stats.pending.toFixed(2)}`}
          icon={<Clock />}
          subtitle={`Next payout: ${stats?.revenue_stats.next_payout_date}`}
        />
      </div>
      
      {/* Revenue Chart */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Revenue Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <RevenueChart data={stats?.revenue_history} />
        </CardContent>
      </Card>
      
      {/* Content Performance */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Top Performing Content</CardTitle>
        </CardHeader>
        <CardContent>
          <ContentPerformanceTable data={stats?.top_content} />
        </CardContent>
      </Card>
      
      {/* Access Logs */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Content Access</CardTitle>
          <CardDescription>AI companies accessing your content</CardDescription>
        </CardHeader>
        <CardContent>
          <AccessLogsTable data={stats?.recent_access} />
        </CardContent>
      </Card>
    </div>
  );
}
```

### Revenue Tracking Component

```typescript
// frontend/components/coalition/RevenueChart.tsx

export function RevenueChart({ data }: { data: RevenueData[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="earned" 
          stroke="#8884d8" 
          name="Earned"
        />
        <Line 
          type="monotone" 
          dataKey="paid" 
          stroke="#82ca9d" 
          name="Paid"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

### Admin Coalition Management

```typescript
// frontend/app/admin/coalition/page.tsx

export default function AdminCoalitionPage() {
  const { data: members } = useCoalitionMembers();
  const { data: agreements } = useLicensingAgreements();
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Coalition Management</h1>
      
      {/* Overview Stats */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Total Members"
          value={members?.total}
          icon={<Users />}
        />
        <StatCard
          title="Active Agreements"
          value={agreements?.active_count}
          icon={<FileText />}
        />
        <StatCard
          title="Total Revenue (MTD)"
          value={`$${agreements?.total_revenue.toLocaleString()}`}
          icon={<DollarSign />}
        />
        <StatCard
          title="Content Pool"
          value={members?.total_content.toLocaleString()}
          icon={<Database />}
        />
      </div>
      
      {/* Tabs */}
      <Tabs defaultValue="members">
        <TabsList>
          <TabsTrigger value="members">Members</TabsTrigger>
          <TabsTrigger value="agreements">Agreements</TabsTrigger>
          <TabsTrigger value="revenue">Revenue</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>
        
        <TabsContent value="members">
          <MembersTable members={members?.data} />
        </TabsContent>
        
        <TabsContent value="agreements">
          <AgreementsTable agreements={agreements?.data} />
        </TabsContent>
        
        <TabsContent value="revenue">
          <RevenueDistributionPanel />
        </TabsContent>
        
        <TabsContent value="analytics">
          <CoalitionAnalytics />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## Backend API Integration

### Coalition Stats Endpoint

```python
# dashboard_app/backend/app/api/v1/coalition.py

from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.services.coalition_service import CoalitionService

router = APIRouter(prefix="/coalition", tags=["coalition"])

@router.get("/stats")
async def get_coalition_stats(
    current_user = Depends(get_current_user)
):
    """Get coalition stats for current user"""
    stats = await CoalitionService.get_member_stats(
        user_id=current_user.id
    )
    return {"success": True, "data": stats}

@router.get("/revenue")
async def get_revenue_breakdown(
    period: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get revenue breakdown"""
    revenue = await CoalitionService.get_member_revenue(
        user_id=current_user.id,
        period=period
    )
    return {"success": True, "data": revenue}

@router.get("/content/performance")
async def get_content_performance(
    limit: int = 10,
    current_user = Depends(get_current_user)
):
    """Get top performing content"""
    content = await CoalitionService.get_top_content(
        user_id=current_user.id,
        limit=limit
    )
    return {"success": True, "data": content}
```

---

## Data Visualization

### Revenue Chart
- **Type**: Line chart
- **X-Axis**: Month
- **Y-Axis**: Revenue (USD)
- **Lines**: Earned vs. Paid
- **Interactivity**: Hover for details

### Content Performance Table
- **Columns**: Title, Type, Word Count, Verifications, Access Count, Revenue
- **Sorting**: By any column
- **Filtering**: By content type, date range
- **Export**: CSV download

### Access Logs Table
- **Columns**: AI Company, Content Title, Access Date, Access Type
- **Pagination**: 50 per page
- **Filtering**: By AI company, date range
- **Real-time**: Auto-refresh every 30s

---

## Rollout Plan

### Week 1: Member Dashboard
- [ ] Coalition stats API integration
- [ ] Stats cards and overview
- [ ] Revenue chart component
- [ ] Basic content performance table

### Week 2: Advanced Features
- [ ] Access logs table
- [ ] Content performance analytics
- [ ] Revenue breakdown by period
- [ ] Export functionality

### Week 3: Admin Features
- [ ] Admin coalition management page
- [ ] Member management table
- [ ] Agreement management interface
- [ ] Revenue distribution controls

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Page load time | <2s |
| User engagement | 60% visit coalition tab weekly |
| Revenue visibility | 100% of members see revenue breakdown |
| Admin efficiency | <5 min to create agreement |

---

## Related PRDs
- **PRD-001**: Coalition Infrastructure
- **PRD-002**: Licensing Agreement Management
- **PRD-003**: WordPress Coalition Integration
