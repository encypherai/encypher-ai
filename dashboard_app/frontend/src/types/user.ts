/**
 * User interface representing the authenticated user data
 */
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * User update data interface
 */
export interface UserUpdateData {
  full_name?: string;
  email?: string;
  username?: string;
}

/**
 * Password change data interface
 */
export interface PasswordChangeData {
  current_password: string;
  new_password: string;
}
