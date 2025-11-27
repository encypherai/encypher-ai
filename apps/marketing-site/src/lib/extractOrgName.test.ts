import { extractOrgName } from './extractOrgName';

describe('extractOrgName', () => {
  it('extracts from standard .com email', () => {
    expect(extractOrgName('user@acme-corp.com')).toBe('acme-corp');
  });
  it('extracts from .org email', () => {
    expect(extractOrgName('user@nonprofit.org')).toBe('nonprofit');
  });
  it('extracts from multi-subdomain email', () => {
    expect(extractOrgName('user@sub.domain.com')).toBe('sub');
  });
  it('extracts from .co.uk email', () => {
    expect(extractOrgName('user@acme.co.uk')).toBe('acme');
  });
  it('returns fallback for invalid email', () => {
    expect(extractOrgName('invalid-email')).toBe('organization');
  });
  it('returns fallback for missing org', () => {
    expect(extractOrgName('user@.com')).toBe('organization');
  });
});
