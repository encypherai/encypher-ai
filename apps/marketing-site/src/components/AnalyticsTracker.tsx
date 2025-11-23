'use client';

import { useEffect, useRef } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { trackEvent } from '@/lib/api';

export function AnalyticsTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const isFirstRender = useRef(true);

  useEffect(() => {
    // Generate a session ID if one doesn't exist
    let sessionId = sessionStorage.getItem('encypher_session_id');
    if (!sessionId) {
      sessionId = crypto.randomUUID();
      sessionStorage.setItem('encypher_session_id', sessionId);
    }

    const url = `${window.location.origin}${pathname}${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;

    trackEvent({
      event_type: 'page_view',
      event_name: 'Page View',
      session_id: sessionId,
      page_url: url,
      page_title: document.title,
      referrer: document.referrer,
      user_agent: navigator.userAgent,
    });

  }, [pathname, searchParams]);

  return null;
}
