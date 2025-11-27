import { trackEvent as apiTrackEvent } from '@/lib/api';

interface AnalyticsEvent {
  event: string;
  properties?: Record<string, any>;
  sessionId?: string;
  timestamp?: number;
}

/**
 * Track an analytics event for the AI demo
 */
export function trackEvent(event: string, properties?: Record<string, any>) {
  if (typeof window === 'undefined') return;

  const sessionId = getSessionId();
  
  const data = {
    event_name: event,
    session_id: sessionId,
    page_url: window.location.href,
    page_title: document.title,
    user_agent: navigator.userAgent,
    referrer: document.referrer,
    properties: {
      ...properties,
      source: 'ai-demo',
      deviceType: getDeviceType(),
    }
  };

  // Send to backend API
  apiTrackEvent(data).catch(console.error);

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[Analytics]', data);
  }
}

/**
 * Track section view
 */
export function trackSectionView(sectionNumber: number, sectionName: string) {
  trackEvent(`section_${sectionNumber}_viewed`, {
    sectionName,
    sectionNumber,
  });
}

/**
 * Track animation completion
 */
export function trackAnimationComplete(animationName: string) {
  trackEvent(`animation_${animationName}_completed`, {
    animationName,
  });
}

/**
 * Track CTA click
 */
export function trackCTAClick(ctaName: string, ctaLocation: string) {
  trackEvent('cta_clicked', {
    ctaName,
    ctaLocation,
  });
}

/**
 * Track scroll milestone
 */
export function trackScrollMilestone(percentage: number) {
  trackEvent(`scroll_${percentage}_percent`, {
    scrollDepth: percentage,
  });
}

/**
 * Get device type based on screen width
 */
function getDeviceType(): 'mobile' | 'tablet' | 'desktop' {
  if (typeof window === 'undefined') return 'desktop';
  
  const width = window.innerWidth;
  if (width < 768) return 'mobile';
  if (width < 1024) return 'tablet';
  return 'desktop';
}

/**
 * Get or create session ID
 */
function getSessionId(): string {
  if (typeof window === 'undefined') return '';

  let sessionId = sessionStorage.getItem('ai_demo_session_id');
  
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('ai_demo_session_id', sessionId);
  }

  return sessionId;
}

/**
 * Track page load
 */
export function trackPageLoad() {
  trackEvent('ai_demo_loaded');
}

/**
 * Track page exit
 */
export function trackPageExit() {
  trackEvent('ai_demo_exit');
}
