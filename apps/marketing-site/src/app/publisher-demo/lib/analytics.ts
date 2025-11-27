// Analytics tracking for publisher demo
import { trackEvent as apiTrackEvent } from '@/lib/api';

interface AnalyticsEvent {
  event: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  properties: Record<string, any>;
  timestamp?: number;
  sessionId?: string;
}

let sessionId: string | null = null;

function getSessionId(): string {
  if (sessionId) return sessionId;
  
  // Generate or retrieve session ID
  if (typeof window !== 'undefined') {
    sessionId = sessionStorage.getItem('publisher_demo_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('publisher_demo_session_id', sessionId);
    }
  }
  
  return sessionId || 'unknown';
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function trackEvent(event: string, properties: Record<string, any> = {}) {
  if (typeof window === 'undefined') return;

  const analyticsEvent = {
    event_name: event,
    session_id: getSessionId(),
    page_url: window.location.href,
    page_title: document.title,
    referrer: document.referrer,
    properties: {
      ...properties,
      source: 'publisher-demo'
    }
  };

  // Skip analytics in development to avoid React Strict Mode double-invokes and 404s
  if (process.env.NODE_ENV === 'development') {
    console.log('[Analytics Event (dev only)]', analyticsEvent);
  }

  // Send to backend API
  apiTrackEvent(analyticsEvent).catch(console.error);
}

export function trackSectionView(sectionNumber: number, sectionName: string) {
  trackEvent(`section_${sectionNumber}_viewed`, {
    sectionName,
  });
}

export function trackAnimationComplete(animationName: string) {
  trackEvent(`${animationName}_animation_completed`, {});
}

export function trackCTAClick(ctaType: string) {
  trackEvent('cta_button_clicked', {
    ctaType,
  });
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function trackFormEvent(eventType: 'opened' | 'submitted' | 'error', details?: any) {
  trackEvent(`demo_form_${eventType}`, details || {});
}
