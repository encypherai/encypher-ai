'use client';

import { useEffect, useRef, useState } from 'react';

export default function ArticleIframe() {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'iframeLoaded') {
        setIsLoaded(true);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const sendMessage = (message: any) => {
    if (iframeRef.current?.contentWindow && isLoaded) {
      iframeRef.current.contentWindow.postMessage(message, '*');
    }
  };

  // Expose sendMessage to parent components via custom event
  useEffect(() => {
    const handleCustomEvent = (event: CustomEvent) => {
      sendMessage(event.detail);
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    window.addEventListener('articleMessage' as any, handleCustomEvent);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return () => window.removeEventListener('articleMessage' as any, handleCustomEvent);
  }, [isLoaded]);

  return (
    <div className="w-full h-full bg-white">
      <iframe
        ref={iframeRef}
        src="/mock-article.html"
        className="w-full h-full border-0"
        title="The Encypher Times Article"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
}

// Helper function to send messages to the article iframe
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function sendArticleMessage(message: any) {
  window.dispatchEvent(new CustomEvent('articleMessage', { detail: message }));
}
