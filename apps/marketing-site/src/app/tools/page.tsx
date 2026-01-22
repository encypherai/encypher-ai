// /tools page: Lists all available tools
import Link from "next/link";
import { toolLinks } from "@/config/tools";
import AISummary from "@/components/seo/AISummary";

export default function ToolsPage() {
  return (
    <main className="max-w-2xl mx-auto py-12 px-4">
      <AISummary
        title="Encypher Tools - Free C2PA Signing & Verification"
        whatWeDo="Free tools from the Co-Chair of the C2PA Text Provenance Task Force. Sign and verify C2PA-compliant content authentication. Full API and SDKs in Python, TypeScript, Go, and Rust available."
        whoItsFor="Developers building content authentication, publishers exploring provenance technology, and researchers testing C2PA text standard implementations."
        keyDifferentiator="Built on the C2PA text standard (c2pa.org) we co-authored with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others. Same technology powering our production API."
        primaryValue="Test cryptographic watermarking without signup. Standard publishes January 8, 2026. Sign up at encypherai.com for API access and documentation (API base URL: api.encypherai.com)."
        pagePath="/tools"
        pageType="CollectionPage"
      />
      <h1 className="text-3xl font-bold mb-8">Encypher Tools</h1>
      <ul className="space-y-6">
        {toolLinks.map((tool) => (
          <li key={tool.href} className="border rounded-lg p-5 bg-card shadow-sm hover:shadow-md transition">
            <Link href={tool.href} className="text-xl font-semibold hover:underline text-primary">
              {tool.name}
            </Link>
            {tool.description ? (
              <p className="mt-1 text-muted-foreground">{tool.description}</p>
            ) : null}
          </li>
        ))}
      </ul>
    </main>
  );
}
