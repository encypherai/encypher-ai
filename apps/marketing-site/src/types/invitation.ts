// Invitation types for API contract

export type InvitationStatus = 'pending' | 'accepted' | 'revoked' | 'expired';

export interface Invitation {
  id: number;
  organization_id: number;
  inviter_id: number;
  invitee_email: string;
  token: string;
  status: InvitationStatus;
  created_at: string;
  expires_at: string;
}

export interface InvitationCreateRequest {
  invitee_email: string;
  expires_at?: string; // ISO8601, optional (default: 7 days)
}

export interface InvitationCreateResponse {
  success: boolean;
  data?: Invitation;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export interface InvitationAcceptRequest {
  token: string;
  password: string;
}

export interface InvitationAcceptResponse {
  success: boolean;
  data?: { user_id: number };
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export interface InvitationDetailsResponse {
  success: boolean;
  data?: {
    organization_name: string;
    inviter_name: string;
    inviter_email: string;
    invitee_email: string;
    status: InvitationStatus;
    expires_at: string;
  };
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
}
