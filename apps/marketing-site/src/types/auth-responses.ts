// Defines the structure of the response from backend's /oauth/exchange and /verify-email endpoints

export interface UserSessionData {
  user_uuid: string;
  email: string;
  roles: string[];
  org_id: number | null;
  org_uuid: string | null;
  org_name: string | null; // Added based on typical needs
  first_name: string | null;
  last_name: string | null;
  name: string | null; // Full name
  provider: string | null; // e.g., 'google', 'github', 'credentials'
  is_verified: boolean; // From User model
  // Add other fields from the backend User model or JWT claims as needed
}

export interface BackendTokenExchangeResponse {
  success: boolean;
  data?: {
    message: string;
    access_token: string;
    token_type: string; // Typically "bearer"
    session_data: UserSessionData;
  };
  error?: {
    code: string; // e.g., "TOKEN_INVALID", "USER_NOT_FOUND"
    message: string;
    details?: any; // For additional error information
  };
}
