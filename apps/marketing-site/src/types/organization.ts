// Typescript types for organization, matching backend schema

export type RevenueTier = "free_agpl" | "growth" | "enterprise";

// Ensure Organization type has id property
export interface Organization {
  id: number;
  uuid: string;
  name: string;
  revenue_tier: RevenueTier;
  primary_contact_email: string;
  address?: string;
  created_at: string;
  updated_at: string;
  latest_org_public_key?: string;
}

export interface OrganizationCreateRequest {
  name: string;
  contact_email: string;
  revenue_tier: RevenueTier;
  address?: string;
}

export interface OrganizationCreateResponse {
  success: boolean;
  data?: {
    organization: Organization;
  };
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}
