/**
 * Extracts the organization name from an email address.
 * The org name is the part after the @ and before the first dot (.)
 * Example: user@acme-corp.com => acme-corp
 * Example: user@sub.domain.com => sub
 * Example: user@acme.co.uk => acme
 *
 * @param email - The user's email address
 * @returns The extracted organization name, or 'organization' if invalid
 */
export function extractOrgName(email: string): string {
  const match = email.match(/@([^.@]+)/);
  return match ? match[1] : 'organization';
}
