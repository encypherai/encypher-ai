import { trackEvent, type AnalyticsEventData } from "@/lib/api";

type StorageLike = Pick<Storage, "getItem" | "setItem">;

type ToolAnalyticsEventInput = {
  eventName: string;
  sessionId: string;
  pageUrl: string;
  pageTitle?: string;
  referrer?: string;
  userAgent?: string;
  properties?: Record<string, unknown>;
};

/** Page context read from window — only available in browser. */
type PageContext = {
  pageUrl: string;
  pageTitle: string;
  referrer: string;
  userAgent: string;
};

const TOOL_SESSION_KEY = "encypher_tools_session_id";

export function getToolSessionId(
  storage: StorageLike | null,
  generateId: () => string
): string {
  if (!storage) {
    return "unknown";
  }

  const existing = storage.getItem(TOOL_SESSION_KEY);
  if (existing) {
    return existing;
  }

  const generated = generateId();
  storage.setItem(TOOL_SESSION_KEY, generated);
  return generated;
}

export function buildToolAnalyticsEvent(
  input: ToolAnalyticsEventInput
): AnalyticsEventData {
  return {
    event_type: "tool_event",
    event_name: input.eventName,
    session_id: input.sessionId,
    page_url: input.pageUrl,
    page_title: input.pageTitle,
    referrer: input.referrer,
    user_agent: input.userAgent,
    properties: input.properties,
  };
}

function defaultIdGenerator(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `tools_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

function readPageContext(): PageContext {
  return {
    pageUrl: window.location.href,
    pageTitle: document.title,
    referrer: document.referrer,
    userAgent: navigator.userAgent,
  };
}

export function trackToolEvent(
  input: Omit<ToolAnalyticsEventInput, "sessionId" | "pageUrl" | "pageTitle" | "referrer" | "userAgent"> & Partial<PageContext>
) {
  if (typeof window === "undefined") {
    return;
  }

  const page = readPageContext();
  const sessionId = getToolSessionId(window.sessionStorage, defaultIdGenerator);
  const payload = buildToolAnalyticsEvent({
    ...page,
    ...input,
    sessionId,
  });

  trackEvent(payload).catch((error) => {
    console.warn("[tools-analytics] failed", error);
  });
}
