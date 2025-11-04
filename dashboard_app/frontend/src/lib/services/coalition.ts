// Re-export coalition service and types
export { default as coalitionService } from '@/services/coalitionService';
export type {
  CoalitionMember,
  CoalitionStats,
  ContentStats,
  RevenueStats,
  RevenueHistoryItem,
  TopContentItem,
  RecentAccessItem,
  ContentItem,
  ContentItemCreate,
  RevenueTransaction,
  AdminCoalitionOverview,
  MemberListItem,
  MemberListResponse
} from '@/services/coalitionService';
