import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Unsubscribe | Encypher',
  description: 'Unsubscribe from the Encypher newsletter.',
  robots: { index: false, follow: false },
};

interface Props {
  searchParams: Promise<{ token?: string }>;
}

async function unsubscribe(token: string): Promise<boolean> {
  const webServiceUrl = process.env.WEB_SERVICE_URL;
  if (!webServiceUrl) {
    return false;
  }
  try {
    const res = await fetch(`${webServiceUrl}/api/v1/newsletter/unsubscribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
      cache: 'no-store',
    });
    return res.ok;
  } catch {
    return false;
  }
}

export default async function UnsubscribePage({ searchParams }: Props) {
  const params = await searchParams;
  const token = params.token;

  let success = false;
  let attempted = false;

  if (token && token.length > 0) {
    attempted = true;
    success = await unsubscribe(token);
  }

  return (
    <div style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '60px 20px' }}>
      <div style={{ maxWidth: '480px', width: '100%', textAlign: 'center' }}>
        {attempted && success ? (
          <>
            <h1 style={{ fontSize: '24px', fontWeight: 600, color: '#1b2f50', marginBottom: '16px' }}>
              You have been unsubscribed
            </h1>
            <p style={{ color: '#475569', fontSize: '16px', lineHeight: '1.6' }}>
              You won&apos;t receive any more emails from us. We&apos;re sorry to see you go.
            </p>
          </>
        ) : (
          <>
            <h1 style={{ fontSize: '24px', fontWeight: 600, color: '#1b2f50', marginBottom: '16px' }}>
              Invalid unsubscribe link
            </h1>
            <p style={{ color: '#475569', fontSize: '16px', lineHeight: '1.6' }}>
              This unsubscribe link is invalid or has already been used.
              If you&apos;re still receiving emails, please contact us at{' '}
              <a href="mailto:contact@encypherai.com" style={{ color: '#2a87c4' }}>
                contact@encypherai.com
              </a>
              .
            </p>
          </>
        )}
      </div>
    </div>
  );
}
