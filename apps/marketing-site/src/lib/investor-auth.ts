/**
 * Investor authentication utilities for managing access tokens
 */

/**
 * Check if the investor token exists and is valid
 * @returns boolean indicating if the token is valid
 */
export function hasValidInvestorToken(): boolean {
  if (typeof window === 'undefined') {
    return false; // Not in browser context
  }

  try {
    // Check if token exists
    const token = sessionStorage.getItem('investorToken');
    if (!token) {
      return false;
    }

    // Check if token is expired
    const expiryStr = sessionStorage.getItem('investorTokenExpiry');
    if (!expiryStr) {
      return false;
    }

    const expiryDate = new Date(expiryStr);
    if (expiryDate < new Date()) {
      // Clear expired tokens
      clearInvestorToken();
      return false;
    }

    return true;
  } catch (error) {
    console.error('Error checking investor token:', error);
    return false;
  }
}

/**
 * Clear all investor token data from session storage
 */
export function clearInvestorToken(): void {
  if (typeof window === 'undefined') {
    return; // Not in browser context
  }

  try {
    sessionStorage.removeItem('investorToken');
    sessionStorage.removeItem('investorTokenExpiry');
    sessionStorage.removeItem('investorId');
  } catch (error) {
    console.error('Error clearing investor token:', error);
  }
}

/**
 * Get the investor token from session storage
 * @returns The investor token or null if not found
 */
export function getInvestorToken(): string | null {
  if (typeof window === 'undefined') {
    return null; // Not in browser context
  }

  try {
    return sessionStorage.getItem('investorToken');
  } catch (error) {
    console.error('Error getting investor token:', error);
    return null;
  }
}

/**
 * Save investor token data to session storage
 * @param token The access token
 * @param expiryDate The expiration date string
 * @param investorId The investor ID
 */
export function saveInvestorToken(token: string, expiryDate: string, investorId?: string): void {
  if (typeof window === 'undefined') {
    return; // Not in browser context
  }

  try {
    sessionStorage.setItem('investorToken', token);
    sessionStorage.setItem('investorTokenExpiry', expiryDate);
    if (investorId) {
      sessionStorage.setItem('investorId', investorId);
    }
  } catch (error) {
    console.error('Error saving investor token:', error);
  }
}
