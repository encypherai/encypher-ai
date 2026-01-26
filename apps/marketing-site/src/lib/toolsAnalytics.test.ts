import { buildToolAnalyticsEvent, getToolSessionId } from "./toolsAnalytics";

describe("toolsAnalytics", () => {
  it("returns existing session id when available", () => {
    const storage = {
      getItem: jest.fn(() => "session-123"),
      setItem: jest.fn(),
    };

    const sessionId = getToolSessionId(storage, () => "generated");

    expect(sessionId).toBe("session-123");
    expect(storage.setItem).not.toHaveBeenCalled();
  });

  it("generates and stores session id when missing", () => {
    const storage = {
      getItem: jest.fn(() => null),
      setItem: jest.fn(),
    };

    const sessionId = getToolSessionId(storage, () => "generated");

    expect(sessionId).toBe("generated");
    expect(storage.setItem).toHaveBeenCalledWith("encypher_tools_session_id", "generated");
  });

  it("returns unknown when storage is unavailable", () => {
    const sessionId = getToolSessionId(null, () => "generated");

    expect(sessionId).toBe("unknown");
  });

  it("builds analytics event payload", () => {
    const event = buildToolAnalyticsEvent({
      eventName: "tools_sign_started",
      sessionId: "session-123",
      pageUrl: "https://encypherai.com/tools/sign-verify",
      pageTitle: "Sign/Verify Tool",
      referrer: "",
      userAgent: "test-agent",
      properties: {
        mode: "sign",
        inputLength: 120,
      },
    });

    expect(event).toEqual({
      event_type: "tool_event",
      event_name: "tools_sign_started",
      session_id: "session-123",
      page_url: "https://encypherai.com/tools/sign-verify",
      page_title: "Sign/Verify Tool",
      referrer: "",
      user_agent: "test-agent",
      properties: {
        mode: "sign",
        inputLength: 120,
      },
    });
  });
});
