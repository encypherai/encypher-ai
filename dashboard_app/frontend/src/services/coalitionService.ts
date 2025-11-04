import api from '@/lib/api';

// Types
export interface CoalitionMember {
  id: number;
  user_id: number;
  status: string;
  joined_date: string;
  total_documents: number;
  total_verifications: number;
  total_earned: number;
  pending_payout: number;
  last_payout_date?: string;
  next_payout_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface ContentStats {
  total_documents: number;
  verification_count: number;
  recent_documents: number;
  trend_percentage: number;
}

export interface RevenueStats {
  total_earned: number;
  pending: number;
  paid: number;
  next_payout_date?: string;
  monthly_average: number;
}

export interface RevenueHistoryItem {
  month: string;
  earned: number;
  paid: number;
}

export interface TopContentItem {
  id: number;
  title: string;
  content_type: string;
  word_count: number;
  verification_count: number;
  access_count: number;
  revenue_generated: number;
}

export interface RecentAccessItem {
  id: number;
  ai_company: string;
  content_title: string;
  access_type: string;
  accessed_at: string;
  revenue_amount: number;
}

export interface CoalitionStats {
  content_stats: ContentStats;
  revenue_stats: RevenueStats;
  revenue_history: RevenueHistoryItem[];
  top_content: TopContentItem[];
  recent_access: RecentAccessItem[];
}

export interface ContentItem {
  id: number;
  user_id: number;
  title: string;
  content_type: string;
  word_count: number;
  file_path?: string;
  c2pa_manifest_url?: string;
  verification_count: number;
  access_count: number;
  revenue_generated: number;
  signed_at: string;
  last_accessed?: string;
  created_at: string;
  updated_at?: string;
}

export interface ContentItemCreate {
  user_id: number;
  title: string;
  content_type: string;
  word_count?: number;
  file_path?: string;
  c2pa_manifest_url?: string;
}

export interface RevenueTransaction {
  id: number;
  user_id: number;
  content_id?: number;
  amount: number;
  transaction_type: string;
  status: string;
  description?: string;
  period_start?: string;
  period_end?: string;
  paid_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface AdminCoalitionOverview {
  total_members: number;
  active_members: number;
  total_content: number;
  total_revenue_mtd: number;
  total_verifications: number;
}

export interface MemberListItem {
  id: number;
  user_id: number;
  email: string;
  full_name: string;
  status: string;
  total_documents: number;
  total_verifications: number;
  total_earned: number;
  pending_payout: number;
  joined_date: string;
}

export interface MemberListResponse {
  items: MemberListItem[];
  total: number;
  page: number;
  limit: number;
}

const coalitionService = {
  /**
   * Get coalition stats for current user
   */
  async getCoalitionStats(): Promise<CoalitionStats> {
    const response = await api.get('/coalition/stats');
    return response.data;
  },

  /**
   * Get revenue breakdown
   */
  async getRevenue(period?: string): Promise<any> {
    const response = await api.get('/coalition/revenue', {
      params: { period }
    });
    return response.data;
  },

  /**
   * Get top performing content
   */
  async getTopContent(limit: number = 10): Promise<ContentItem[]> {
    const response = await api.get('/coalition/content/performance', {
      params: { limit }
    });
    return response.data;
  },

  /**
   * Create a new content item
   */
  async createContent(contentData: ContentItemCreate): Promise<ContentItem> {
    const response = await api.post('/coalition/content', contentData);
    return response.data;
  },

  /**
   * Get coalition member info
   */
  async getMemberInfo(): Promise<CoalitionMember> {
    const response = await api.get('/coalition/member');
    return response.data;
  },

  // Admin methods
  /**
   * Get admin coalition overview
   */
  async getAdminOverview(): Promise<AdminCoalitionOverview> {
    const response = await api.get('/coalition/admin/overview');
    return response.data;
  },

  /**
   * Get list of coalition members (admin)
   */
  async getMembers(skip: number = 0, limit: number = 50): Promise<MemberListResponse> {
    const response = await api.get('/coalition/admin/members', {
      params: { skip, limit }
    });
    return response.data;
  },
};

export default coalitionService;
