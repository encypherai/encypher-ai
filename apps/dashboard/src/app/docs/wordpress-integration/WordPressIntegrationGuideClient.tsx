'use client';

import Link from 'next/link';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useEffect, useMemo, useState } from 'react';
import { Check, Copy, Download, ExternalLink } from 'lucide-react';

function stripEmojis(input: string): string {
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

export function WordPressIntegrationGuideClient({ markdown }: { markdown: string }) {
  const [activeSection, setActiveSection] = useState<string>('');
  const NAV_OFFSET_PX = 72;

  const sanitizedMarkdown = useMemo(() => stripEmojis(markdown), [markdown]);

  const tableOfContents: TocItem[] = useMemo(() => {
    const items: TocItem[] = [];
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
          <li>
            <Link href="/docs/publisher-integration" className="hover:text-blue-ncs transition-colors">
              Publisher Integration
            </Link>
          </li>
          <li>/</li>
          <li className="text-delft-blue dark:text-white font-medium">WordPress</li>
        </ol>
      </nav>

      <div className="flex flex-col lg:flex-row gap-12">
        {/* Main Content */}
        <article className="flex-1 min-w-0">
          <header className="mb-12">
            <div className="flex items-center gap-3 mb-4">
              <span className="p-2 bg-[#21759b]/10 text-[#21759b] rounded-lg">
                <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                  <path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zM3.009 12c0-1.298.29-2.529.8-3.64l4.404 12.065A8.993 8.993 0 013.009 12zm8.991 9c-.924 0-1.813-.15-2.646-.42l2.81-8.162 2.878 7.886c.019.046.042.089.065.13A8.94 8.94 0 0112 21zm1.237-13.22c.564-.03 1.072-.09 1.072-.09.505-.06.446-.802-.059-.772 0 0-1.518.12-2.497.12-.921 0-2.468-.12-2.468-.12-.505-.03-.564.742-.059.772 0 0 .478.06.983.09l1.46 4.002-2.052 6.155-3.413-10.157c.564-.03 1.072-.09 1.072-.09.505-.06.446-.802-.06-.772 0 0-1.517.12-2.496.12-.176 0-.383-.005-.6-.013A8.977 8.977 0 0112 3.009c2.34 0 4.472.895 6.071 2.36-.039-.002-.076-.008-.116-.008-1.005 0-1.716.875-1.716 1.817 0 .843.487 1.557 1.005 2.4.39.675.843 1.54.843 2.79 0 .867-.333 1.872-.773 3.272l-1.013 3.383L12.237 7.78z" />
                </svg>
              </span>
              <span className="text-sm font-semibold uppercase tracking-wider text-[#21759b]">WordPress Plugin</span>
            </div>
            <h1 className="text-4xl font-extrabold text-delft-blue dark:text-white mb-4 tracking-tight leading-tight">
              WordPress Integration Guide
            </h1>
            <p className="text-xl text-slate-500 dark:text-slate-400 max-w-3xl leading-relaxed mb-8">
              Step-by-step guide to installing and configuring the Encypher Provenance plugin for WordPress.
            </p>

            {/* Quick Action Card */}
            <div className="flex flex-wrap gap-4 mb-8">
              <a
                href="/downloads/encypher-provenance.zip"
                className="inline-flex items-center gap-2 px-5 py-3 bg-[#21759b] text-white rounded-xl font-semibold hover:bg-[#1a5f7a] transition-colors shadow-lg shadow-[#21759b]/20"
              >
                <Download className="w-5 h-5" />
                Download Plugin
              </a>
              <Link
                href="/api-keys"
                className="inline-flex items-center gap-2 px-5 py-3 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-xl font-semibold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              >
                Get API Key
                <ExternalLink className="w-4 h-4" />
              </Link>
            </div>

            {/* Time Estimate */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-lg text-sm font-medium">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Setup time: ~5 minutes
            </div>
          </header>

          <div
            className="prose prose-slate dark:prose-invert max-w-none
              prose-headings:scroll-mt-[72px]
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
              prose-td:px-4 prose-td:py-4 prose-td:text-sm prose-td:border-b prose-td:border-slate-100 dark:prose-td:border-slate-800/50 last:prose-td:border-b-0
              prose-img:rounded-xl prose-img:shadow-lg prose-img:border prose-img:border-slate-200 dark:prose-img:border-slate-800"
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
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-blue-ncs bg-blue-50 dark:bg-blue-900/20 pl-4 py-3 pr-4 my-6 rounded-r-lg text-slate-700 dark:text-slate-300 not-italic">
                    {children}
                  </blockquote>
                ),
                img: ({ src, alt }) => {
                  if (!src) return null;
                  return (
                    <div className="my-8">
                      <div className="relative rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-lg bg-slate-100 dark:bg-slate-800">
                        <div className="flex items-center gap-2 px-4 py-2 bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
                          <div className="flex gap-1.5">
                            <div className="w-3 h-3 rounded-full bg-red-400" />
                            <div className="w-3 h-3 rounded-full bg-yellow-400" />
                            <div className="w-3 h-3 rounded-full bg-green-400" />
                          </div>
                          <span className="text-xs text-slate-400 ml-2">{alt}</span>
                        </div>
                        <div className="p-4 flex items-center justify-center min-h-[200px] text-slate-400 text-sm">
                          <div className="text-center">
                            <svg className="w-12 h-12 mx-auto mb-2 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <p className="font-medium">{alt || 'Screenshot'}</p>
                            <p className="text-xs mt-1">Screenshot coming soon</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                },
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
                    <Link href={href || '#'} className="text-blue-ncs hover:underline">
                      {children}
                    </Link>
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
          <div className="sticky top-20 p-6 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-4">On this page</h4>
            <nav className="space-y-1 max-h-[60vh] overflow-y-auto">
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

            <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800 space-y-3">
              <a
                href="/downloads/encypher-provenance.zip"
                className="flex items-center justify-center gap-2 p-3 rounded-lg bg-[#21759b] text-white hover:bg-[#1a5f7a] transition-all text-sm font-semibold"
              >
                <Download className="w-4 h-4" />
                Download Plugin
              </a>
              <a
                href="/docs/publisher-integration"
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
                  API Guide
                </div>
                <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
            </div>
          </div>
        </aside>
      </div>
    </>
  );
}
