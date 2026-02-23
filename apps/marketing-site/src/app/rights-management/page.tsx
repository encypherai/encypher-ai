import { NextPage } from 'next';
import Link from 'next/link';
import AISummary from '@/components/seo/AISummary';

const RightsManagementPage: NextPage = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <AISummary
        title="Rights Management — Machine-Readable Licensing for the AI Age"
        whatWeDo="Publisher-controlled licensing terms embedded cryptographically in every piece of content. Bronze (crawling), Silver (RAG), Gold (training) tiers. Formal notice system establishes willful infringement. Evidence packages provide court-ready proof."
        whoItsFor="Publishers, media organizations, and content creators who want to control how their content is used by AI companies. AI companies who want to license content at scale with machine-readable terms."
        keyDifferentiator="Every signed document embeds a rights_resolution_url. AI crawlers that resolve this URL receive machine-readable licensing terms. The three-tier model aligns with how AI companies actually use content."
        primaryValue="Transform unauthorized AI use from innocent mistake to willful infringement. Establish a formal licensing framework backed by cryptographic proof."
      />

      {/* Hero */}
      <section className="pt-20 pb-16 px-4 sm:px-6 lg:px-8 text-center bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-950">
        <div className="max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 text-sm font-medium mb-6">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            Machine-Readable Licensing
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 dark:text-slate-100 mb-6 leading-tight">
            License Your Content<br />
            <span className="text-[#2A87C4]">to the AI Age</span>
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-10">
            Every document you sign embeds machine-readable licensing terms. AI companies discover your terms automatically. You control scraping, RAG, and training — separately.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link
              href="/dashboard/rights"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[#2A87C4] text-white font-semibold hover:bg-[#1b6fa8] transition-colors shadow-sm"
            >
              Set Up Your Rights Profile
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
            <a
              href="#how-it-works"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              How it works
            </a>
          </div>
        </div>
      </section>

      {/* Three tier cards */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white dark:bg-slate-950">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center text-slate-900 dark:text-slate-100 mb-3">Three Tiers, Three Use Cases</h2>
          <p className="text-slate-500 dark:text-slate-400 text-center mb-10 max-w-2xl mx-auto">
            Control AI access to your content at three distinct levels, each aligned to how AI companies actually use content.
          </p>
          <div className="grid gap-6 md:grid-cols-3">
            {/* Bronze */}
            <div className="rounded-2xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/20 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900 flex items-center justify-center">
                  <span className="text-xl">&#x1F949;</span>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-slate-100">Bronze</h3>
                  <p className="text-xs text-amber-700 dark:text-amber-400">Crawling &amp; Scraping</p>
                </div>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">Controls broad read-only access: search indexing, price comparisons, web archiving, and general AI data collection.</p>
              <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-400">
                <li className="flex gap-2"><span className="text-amber-500">&bull;</span> Web crawlers (Googlebot, GPTBot)</li>
                <li className="flex gap-2"><span className="text-amber-500">&bull;</span> Training data collection</li>
                <li className="flex gap-2"><span className="text-amber-500">&bull;</span> RSS/feed aggregation</li>
                <li className="flex gap-2"><span className="text-amber-500">&bull;</span> robots.txt-aligned signals</li>
              </ul>
            </div>
            {/* Silver */}
            <div className="rounded-2xl border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-800/40 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                  <span className="text-xl">&#x1F948;</span>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-slate-100">Silver</h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400">RAG &amp; Retrieval</p>
                </div>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">Controls AI-powered search and retrieval-augmented generation pipelines — the largest current use case.</p>
              <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-400">
                <li className="flex gap-2"><span className="text-slate-400">&bull;</span> RAG grounding data</li>
                <li className="flex gap-2"><span className="text-slate-400">&bull;</span> Real-time AI search</li>
                <li className="flex gap-2"><span className="text-slate-400">&bull;</span> Perplexity, SearchGPT, Bing AI</li>
                <li className="flex gap-2"><span className="text-slate-400">&bull;</span> Enterprise AI assistants</li>
              </ul>
            </div>
            {/* Gold */}
            <div className="rounded-2xl border border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-950/20 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-yellow-100 dark:bg-yellow-900 flex items-center justify-center">
                  <span className="text-xl">&#x1F947;</span>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-slate-100">Gold</h3>
                  <p className="text-xs text-yellow-700 dark:text-yellow-400">Training &amp; Fine-tuning</p>
                </div>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">Controls use of your content for AI model training and fine-tuning — the highest-value licensing category.</p>
              <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-400">
                <li className="flex gap-2"><span className="text-yellow-500">&bull;</span> LLM pre-training datasets</li>
                <li className="flex gap-2"><span className="text-yellow-500">&bull;</span> Fine-tuning &amp; RLHF</li>
                <li className="flex gap-2"><span className="text-yellow-500">&bull;</span> Model evaluation benchmarks</li>
                <li className="flex gap-2"><span className="text-yellow-500">&bull;</span> Synthetic data generation</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-16 px-4 sm:px-6 lg:px-8 bg-slate-50 dark:bg-slate-900">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-center text-slate-900 dark:text-slate-100 mb-10">How It Works</h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { step: '1', icon: '\u270D\uFE0F', title: 'Sign', desc: 'Publish content with Encypher. Every document gets a cryptographic signature with rights_resolution_url embedded.' },
              { step: '2', icon: '\uD83D\uDCCB', title: 'Publish Profile', desc: 'Set your Bronze/Silver/Gold terms once. They apply to all signed content automatically.' },
              { step: '3', icon: '\uD83E\uDD16', title: 'AI Discovers', desc: 'AI crawlers resolve the rights URL. Machine-readable terms tell them exactly what requires a license.' },
              { step: '4', icon: '\uD83D\uDCB0', title: 'License or Notice', desc: 'Compliant AI companies license through the coalition. Non-compliant ones face formal infringement notice.' },
            ].map(item => (
              <div key={item.step} className="text-center">
                <div className="w-14 h-14 rounded-2xl bg-white dark:bg-slate-800 shadow-sm flex items-center justify-center mx-auto mb-3 text-2xl">
                  {item.icon}
                </div>
                <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Formal Notice section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white dark:bg-slate-950">
        <div className="max-w-4xl mx-auto grid gap-10 lg:grid-cols-2 items-center">
          <div>
            <div className="text-xs font-semibold text-red-600 dark:text-red-400 uppercase tracking-wide mb-3">Enforcement</div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4">
              Transform Unauthorized Use into Willful Infringement
            </h2>
            <p className="text-slate-600 dark:text-slate-400 mb-4">
              AI companies can no longer claim ignorance. When your rights profile is embedded in every signed document, using your content without a license is knowingly ignoring machine-readable terms.
            </p>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              Issue a formal notice at any time. Our cryptographic evidence system creates an immutable record: when you published it, when they accessed it, and that your terms were available and ignored.
            </p>
            <ul className="space-y-2 text-sm">
              {[
                'Immutable notice with tamper-evident evidence chain',
                'Delivery confirmation and timestamped proof of receipt',
                'Documentation of marked content in their pipeline',
                'Chain-of-custody from signing through detection',
              ].map(item => (
                <li key={item} className="flex gap-2 text-slate-700 dark:text-slate-300">
                  <svg className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-2xl border border-red-100 dark:border-red-900 bg-red-50 dark:bg-red-950/20 p-6">
            <p className="text-sm font-semibold text-red-800 dark:text-red-300 mb-2">Formal Notice Package — $499/notice</p>
            <p className="text-xs text-red-600 dark:text-red-400 mb-4">One-time fee per formal notice issued to a specific AI company.</p>
            <div className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
              <p>&#x2726; Cryptographically-backed notice letter</p>
              <p>&#x2726; Verification API access instructions for recipient</p>
              <p>&#x2726; Evidence of marked content in training pipeline</p>
              <p>&#x2726; Tamper-evident delivery receipt</p>
            </div>
          </div>
        </div>
      </section>

      {/* Evidence Package */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-slate-50 dark:bg-slate-900">
        <div className="max-w-4xl mx-auto grid gap-10 lg:grid-cols-2 items-center">
          <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6">
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-4">Evidence Package — $999/package</p>
            <div className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
              <p>&#x2726; Merkle tree proofs — sentence-level provenance</p>
              <p>&#x2726; Chain-of-custody documentation</p>
              <p>&#x2726; Tamper-evident manifest records</p>
              <p>&#x2726; Formal notice delivery records</p>
              <p>&#x2726; Timeline reconstruction</p>
              <p>&#x2726; Cryptographic verification instructions for counsel</p>
              <p>&#x2726; Export in standard litigation support formats</p>
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-3">Litigation Ready</div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4">
              Court-Ready Evidence in Minutes
            </h2>
            <p className="text-slate-600 dark:text-slate-400">
              Generate a complete evidence package for any infringement claim. Merkle proofs establish sentence-level provenance from the moment of signing. Every event in the chain is cryptographically linked.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing table */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white dark:bg-slate-950">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-center text-slate-900 dark:text-slate-100 mb-3">Simple, Transparent Pricing</h2>
          <p className="text-slate-500 dark:text-slate-400 text-center mb-10">Free signing infrastructure. Paid only for enforcement tools.</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <thead className="bg-slate-50 dark:bg-slate-800">
                <tr>
                  <th className="text-left px-5 py-3 text-slate-600 dark:text-slate-400 font-medium">Feature</th>
                  <th className="text-right px-5 py-3 text-slate-600 dark:text-slate-400 font-medium">Price</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {[
                  { feature: 'Document signing (C2PA 2.3)', price: 'Free (1,000/mo)' },
                  { feature: 'Rights profile (Bronze/Silver/Gold)', price: 'Free' },
                  { feature: 'Public rights resolution URL', price: 'Free' },
                  { feature: 'Coalition enrollment &amp; content indexing', price: 'Free' },
                  { feature: 'Attribution Analytics dashboard', price: '$299/mo' },
                  { feature: 'Formal Notice Package', price: '$499/notice' },
                  { feature: 'Evidence Package', price: '$999/package' },
                  { feature: 'Enforcement Bundle (all enforcement tools)', price: '$999/mo — save 57%' },
                ].map(row => (
                  <tr key={row.feature} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <td className="px-5 py-3 text-slate-700 dark:text-slate-300" dangerouslySetInnerHTML={{ __html: row.feature }} />
                    <td className="px-5 py-3 text-right font-medium text-slate-900 dark:text-slate-100">{row.price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-6 p-4 rounded-xl bg-blue-50 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900 text-sm text-blue-700 dark:text-blue-300">
            <strong>Coalition licensing revenue:</strong> When AI companies license content through the Encypher Coalition, the majority of revenue goes to publishers. Same splits for all tiers -- contact us for details.
          </div>
        </div>
      </section>

      {/* For AI Companies */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-[#1b2f50]">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-white mb-4">For AI Companies</h2>
          <p className="text-slate-300 mb-10 max-w-2xl mx-auto">
            Access machine-readable licensing terms for every Encypher-signed publisher. Build your provenance infrastructure once, stay compliant across the entire ecosystem.
          </p>
          <div className="grid gap-6 sm:grid-cols-3 text-left">
            {[
              { icon: '\uD83D\uDD0D', title: 'Quote Integrity API', desc: 'Verify AI attribution accuracy before publishing. Prove whether a cited quote is accurate, approximate, or hallucinated.' },
              { icon: '\uD83D\uDCDC', title: 'Machine-Readable Terms', desc: 'GET /public/rights/organization/{id} returns W3C ODRL-compatible licensing terms. RSL 1.0 XML available.' },
              { icon: '\uD83E\uDD1D', title: 'Coalition Licensing', desc: 'Single agreement covers all coalition publishers. Structured licensing at scale, not 1:1 negotiations.' },
            ].map(item => (
              <div key={item.title} className="rounded-xl bg-white/5 border border-white/10 p-5">
                <div className="text-2xl mb-3">{item.icon}</div>
                <h3 className="font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-slate-300">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 text-center bg-gradient-to-b from-white to-slate-50 dark:from-slate-950 dark:to-slate-900">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-4">Ready to Take Control?</h2>
          <p className="text-slate-500 dark:text-slate-400 mb-8">
            Set up your rights profile in minutes. Free to start. Enforcement tools available when you need them.
          </p>
          <Link
            href="/dashboard/rights"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-[#2A87C4] text-white font-semibold hover:bg-[#1b6fa8] transition-colors shadow-lg text-lg"
          >
            Set Up Your Rights Profile
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default RightsManagementPage;
