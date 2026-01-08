'use client';

import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useEffect, useMemo, useState } from 'react';
import { Check, Copy } from 'lucide-react';

function stripEmojis(input: string): string {
  // Strip common emoji ranges. This is intentionally conservative.
  // Keeps punctuation like "#" used for anchor links.
  return input.replace(
    /[\u{1F300}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu,
    ''
  );
}

const CodeBlock = ({ children, language }: { children: string; language?: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group/code">
      <button
        onClick={handleCopy}
        className="absolute right-3 top-3 p-2 rounded-md bg-slate-800/50 border border-slate-700 opacity-0 group-hover/code:opacity-100 transition-opacity hover:bg-slate-700"
        title="Copy code"
      >
        {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4 text-slate-400" />}
      </button>
      <SyntaxHighlighter
        style={oneDark}
        language={language}
        PreTag="div"
        customStyle={{
          margin: 0,
          borderRadius: '0.75rem',
          fontSize: '0.875rem',
          padding: '1.5rem',
          backgroundColor: '#0f172a',
        }}
      >
        {children.replace(/\n$/, '')}
      </SyntaxHighlighter>
    </div>
  );
};

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

type TocItem = { id: string; title: string };

export function PublisherIntegrationGuideClient({ markdown }: { markdown: string }) {
  const [activeSection, setActiveSection] = useState<string>('');
  const NAV_OFFSET_PX = 120;

  const sanitizedMarkdown = useMemo(() => stripEmojis(markdown), [markdown]);

  const tableOfContents: TocItem[] = useMemo(() => {
    const items: TocItem[] = [];
    // Capture h2 only for sidebar.
    for (const match of sanitizedMarkdown.matchAll(/^##\s+(.+)$/gm)) {
      const title = match[1]?.trim();
      if (!title) continue;
      items.push({ id: slugify(title), title });
    }
    return items;
  }, [sanitizedMarkdown]);

  useEffect(() => {
    const handleScroll = () => {
      const headings = document.querySelectorAll('h2[id]');
      if (headings.length === 0) return;

      const scrollPosition = window.scrollY + 150;
      let currentId = '';

      headings.forEach((heading) => {
        const element = heading as HTMLElement;
        if (element.offsetTop <= scrollPosition) {
          currentId = element.id;
        }
      });

      if (currentId) {
        setActiveSection(currentId);
      }
    };

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    const timeoutId = setTimeout(handleScroll, 200);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      clearTimeout(timeoutId);
    };
  }, []);

  const scrollToId = (id: string) => {
    const target = document.getElementById(id);
    if (!target) return;

    const top = target.getBoundingClientRect().top + window.scrollY - NAV_OFFSET_PX;
    window.scrollTo({ top, behavior: 'smooth' });
    window.history.pushState(null, '', `#${id}`);
  };

  return (
    <>
      {/* Breadcrumb */}
      <nav className="mb-6">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground">
          <li>
            <Link href="/docs" className="hover:text-blue-ncs transition-colors">
              Documentation
            </Link>
          </li>
          <li>/</li>
          <li className="text-delft-blue dark:text-white font-medium">Publisher Integration Guide</li>
        </ol>
      </nav>

      <div className="flex flex-col lg:flex-row gap-12">
        {/* Main Content */}
        <article className="flex-1 min-w-0">
          <header className="mb-12">
            <div className="flex items-center gap-3 mb-4">
              <span className="p-2 bg-blue-ncs/10 text-blue-ncs rounded-lg">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
                  />
                </svg>
              </span>
              <span className="text-sm font-semibold uppercase tracking-wider text-blue-ncs">Integration Guide</span>
            </div>
            <h1 className="text-4xl font-extrabold text-delft-blue dark:text-white mb-4 tracking-tight leading-tight">
              Publisher Integration Guide
            </h1>
            <p className="text-xl text-slate-500 dark:text-slate-400 max-w-3xl leading-relaxed mb-8">
              Add C2PA content authentication to your CMS or publishing workflow. Choose your tier below to see what's available.
            </p>
          </header>

          <div
            className="prose prose-slate dark:prose-invert max-w-none 
              prose-headings:scroll-mt-28
              prose-h2:text-2xl prose-h2:font-bold prose-h2:mt-16 prose-h2:mb-6 prose-h2:pb-2 prose-h2:border-b prose-h2:border-slate-200 dark:prose-h2:border-slate-800
              prose-h3:text-xl prose-h3:font-semibold prose-h3:mt-10 prose-h3:mb-4
              prose-p:text-slate-600 dark:prose-p:text-slate-400 prose-p:leading-8 prose-p:mb-6
              prose-strong:text-slate-900 dark:prose-strong:text-white
              prose-a:text-blue-ncs prose-a:no-underline hover:prose-a:underline
              prose-code:before:content-none prose-code:after:content-none
              prose-hr:my-12 prose-hr:border-slate-200 dark:prose-hr:border-slate-800
              prose-table:my-8 prose-table:border-separate prose-table:border-spacing-0 prose-table:rounded-xl prose-table:border prose-table:border-slate-200 dark:prose-table:border-slate-800 prose-table:overflow-hidden
              prose-thead:bg-slate-50 dark:prose-thead:bg-slate-800/50
              prose-th:px-4 prose-th:py-3 prose-th:text-left prose-th:text-xs prose-th:font-semibold prose-th:uppercase prose-th:tracking-wider prose-th:text-slate-500 dark:prose-th:text-slate-400 prose-th:border-b prose-th:border-slate-200 dark:prose-th:border-slate-800
              prose-td:px-4 prose-td:py-4 prose-td:text-sm prose-td:border-b prose-td:border-slate-100 dark:prose-td:border-slate-800/50 last:prose-td:border-b-0"
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: () => null,
                h2: ({ children }) => {
                  const id = slugify(children?.toString() || '');
                  return (
                    <h2 id={id} className="group relative">
                      <a
                        href={`#${id}`}
                        onClick={(e) => {
                          e.preventDefault();
                          scrollToId(id);
                        }}
                        className="absolute -left-6 top-0 opacity-0 group-hover:opacity-100 text-slate-300 dark:text-slate-600 transition-opacity pr-2"
                        aria-hidden="true"
                      >
                        #
                      </a>
                      {children}
                    </h2>
                  );
                },
                h3: ({ children }) => {
                  const id = slugify(children?.toString() || '');
                  return (
                    <h3 id={id} className="group relative">
                      <a
                        href={`#${id}`}
                        onClick={(e) => {
                          e.preventDefault();
                          scrollToId(id);
                        }}
                        className="absolute -left-5 top-0 opacity-0 group-hover:opacity-100 text-slate-300 dark:text-slate-600 transition-opacity pr-2 text-base"
                        aria-hidden="true"
                      >
                        #
                      </a>
                      {children}
                    </h3>
                  );
                },
                ul: ({ children }) => (
                  <ul className="list-disc pl-6 my-6 text-slate-600 dark:text-slate-400">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-6 my-6 text-slate-600 dark:text-slate-400">{children}</ol>
                ),
                li: ({ children }) => <li className="my-1 leading-7">{children}</li>,
                code: ({ className, children }) => {
                  const match = /language-(\w+)/.exec(className || '');
                  const isInline = !match;

                  if (isInline) {
                    return (
                      <code className="bg-slate-100 dark:bg-slate-800 text-blue-ncs px-1.5 py-0.5 rounded text-sm font-medium">
                        {children}
                      </code>
                    );
                  }

                  return (
                    <div className="my-6">
                      <CodeBlock language={match?.[1]}>{String(children)}</CodeBlock>
                    </div>
                  );
                },
                a: ({ href, children }) => {
                  const isExternal = href?.startsWith('http');
                  if (isExternal) {
                    return (
                      <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-ncs hover:underline">
                        {children}
                      </a>
                    );
                  }
                  return (
                    <a href={href} className="text-blue-ncs hover:underline">
                      {children}
                    </a>
                  );
                },
                table: ({ children }) => (
                  <div className="my-8 overflow-x-auto">
                    <table className="w-full border-separate border-spacing-0 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-slate-50 dark:bg-slate-800/50">{children}</thead>
                ),
                th: ({ children }) => (
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-4 py-4 text-sm border-b border-slate-100 dark:border-slate-800/50">
                    {children}
                  </td>
                ),
                tr: ({ children }) => <tr className="last:[&>td]:border-b-0">{children}</tr>,
              }}
            >
              {sanitizedMarkdown}
            </ReactMarkdown>
          </div>
        </article>

        {/* Table of Contents Sidebar */}
        <aside className="hidden xl:block w-72 flex-shrink-0">
          <div className="sticky top-28 p-6 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-4">On this page</h4>
            <nav className="space-y-1">
              {tableOfContents.map((item) => (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  onClick={(e) => {
                    e.preventDefault();
                    scrollToId(item.id);
                  }}
                  className={`group flex items-center gap-3 text-sm py-2 px-3 rounded-lg transition-all ${
                    activeSection === item.id
                      ? 'bg-white dark:bg-slate-800 text-blue-ncs font-semibold shadow-sm border border-slate-200 dark:border-slate-700'
                      : 'text-slate-500 dark:text-slate-400 hover:text-delft-blue dark:hover:text-white'
                  }`}
                >
                  <div
                    className={`w-1 h-1 rounded-full transition-all ${
                      activeSection === item.id
                        ? 'bg-blue-ncs scale-150'
                        : 'bg-slate-300 dark:bg-slate-700 group-hover:bg-slate-400'
                    }`}
                  />
                  {item.title}
                </a>
              ))}
            </nav>

            <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800">
              <a
                href="https://api.encypherai.com/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between group p-3 rounded-lg border border-dashed border-slate-300 dark:border-slate-700 hover:border-blue-ncs hover:bg-blue-ncs/5 transition-all text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-blue-ncs"
              >
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                  API Reference
                </div>
                <svg
                  className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
              </a>
            </div>
          </div>
        </aside>
      </div>
    </>
  );
}
