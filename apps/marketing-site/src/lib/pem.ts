// PEM formatting utility for Ed25519 keys
// Usage: toPem(key: string, type: 'private' | 'public')

export function toPem(keyBase64: string, type: 'private' | 'public'): string {
  // PEM headers/footers
  const header = type === 'private'
    ? '-----BEGIN PRIVATE KEY-----'
    : '-----BEGIN PUBLIC KEY-----';
  const footer = type === 'private'
    ? '-----END PRIVATE KEY-----'
    : '-----END PUBLIC KEY-----';
  // Insert line breaks every 64 chars for PEM readability
  const body = keyBase64.replace(/(.{64})/g, '$1\n');
  return `${header}\n${body}\n${footer}\n`;
}
