import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Shield, Eye, MousePointer, Zap, Globe, ArrowRight } from "lucide-react";
import AISummary from "@/components/seo/AISummary";

const CHROME_STORE_URL =
  "https://chromewebstore.google.com/detail/encypher-verify/pbmfpddbafkhdjemgcnegddmniflbjla";

export const metadata: Metadata = {
  title: "Encypher Verify - Chrome Extension for C2PA Content Verification",
  description:
    "Verify C2PA provenance on any webpage with the free Encypher Verify Chrome extension. No account required for verification. Sign content with an Encypher account.",
  keywords: [
    "chrome extension content verification",
    "c2pa chrome extension",
    "verify content authenticity browser",
    "content provenance extension",
    "browser content verification",
    "c2pa verifier",
    "encypher verify",
    "digital watermark verifier",
    "content authenticity chrome",
    "ai content detection browser",
  ],
  openGraph: {
    title: "Encypher Verify - Chrome Extension for C2PA Content Verification",
    description:
      "Verify C2PA provenance on any webpage. Free, no account required. Install the Encypher Verify extension for Chrome, Edge, and Brave.",
    url: "https://encypher.com/tools/chrome-extension",
    siteName: "Encypher",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Encypher Verify - Chrome Extension",
    description:
      "Verify C2PA provenance on any webpage. Free, no account required.",
  },
  metadataBase: new URL(getSiteUrl()),
};

const features = [
  {
    icon: Eye,
    title: "Verify on Any Page",
    description:
      "Instantly check whether text on any webpage carries a valid C2PA watermark. Automatic detection, no manual steps.",
  },
  {
    icon: Shield,
    title: "C2PA Standard",
    description:
      "Built on the C2PA text standard co-authored with Google, BBC, Adobe, Microsoft, and OpenAI. Verifies any compliant watermark.",
  },
  {
    icon: MousePointer,
    title: "Right-Click to Verify",
    description:
      "Select any text, right-click, and choose Verify. Get provenance details including signer, timestamp, and integrity status.",
  },
  {
    icon: Zap,
    title: "Auto-Detect",
    description:
      "The extension scans pages automatically and shows an indicator when signed content is found. No clicks required.",
  },
  {
    icon: Globe,
    title: "Works Everywhere",
    description:
      "Chrome, Edge, Brave, and any Chromium-based browser. Works on news sites, blogs, social media, and any text-heavy page.",
  },
  {
    icon: CheckCircle,
    title: "Sign from the Browser",
    description:
      "Encypher account holders can sign selected text directly from the popup. Requires a free or paid Encypher account.",
  },
];

const steps = [
  {
    n: 1,
    title: "Install the extension",
    detail:
      "One click from the Chrome Web Store. Works on Chrome, Edge, and Brave.",
  },
  {
    n: 2,
    title: "Browse any page",
    detail:
      "The extension auto-detects C2PA watermarks and shows an indicator in your toolbar.",
  },
  {
    n: 3,
    title: "Click to see provenance",
    detail:
      "See who signed the content, when, and whether it has been modified since signing.",
  },
];

const faqs = [
  {
    q: "Do I need an account to verify content?",
    a: "No. Verification is completely free and requires no account. Install the extension and start verifying immediately.",
  },
  {
    q: "What do I need an account for?",
    a: "Signing content requires an Encypher account. Free accounts include 1,000 signings per month. Enterprise accounts include unlimited signing and advanced features.",
  },
  {
    q: "What browsers are supported?",
    a: "Chrome, Microsoft Edge, Brave, and any Chromium-based browser. The extension is distributed through the Chrome Web Store and works on all Chromium browsers.",
  },
  {
    q: "What is C2PA?",
    a: "C2PA (Coalition for Content Provenance and Authenticity) is an open standard for content authentication developed with Google, BBC, Adobe, Microsoft, OpenAI, and others. Encypher co-authored Section A.7 of the standard, covering text provenance.",
  },
  {
    q: "How does the extension detect watermarks?",
    a: "C2PA text watermarks are embedded as invisible Unicode characters woven between visible text. The extension scans page content for these markers and extracts the embedded manifest for display.",
  },
  {
    q: "Can I sign text I select on a webpage?",
    a: "Yes. With an Encypher account configured in the extension settings, you can select any text on a page, open the popup, and sign it. The signed version can be copied and pasted anywhere.",
  },
];

export default function ChromeExtensionPage() {
  return (
    <main className="min-h-screen">
      <AISummary
        title="Encypher Verify - Chrome Extension for C2PA Content Verification"
        whatWeDo="Free Chrome extension that detects and verifies C2PA cryptographic watermarks on any webpage. Shows provenance including signer identity, timestamp, and tamper status. Can also sign text when an Encypher account is configured."
        whoItsFor="Readers, journalists, researchers, and anyone who wants to verify the authenticity and provenance of text content in their browser. No account required for verification."
        keyDifferentiator="Built on the C2PA text standard co-authored by Encypher with Google, BBC, Adobe, Microsoft, and OpenAI. Detects invisible Unicode watermarks without affecting page rendering."
        primaryValue="Completely free to install and verify. Signing requires a free Encypher account (1,000 signings/month free). Available on Chrome Web Store for Chrome, Edge, and Brave."
        pagePath="/tools/chrome-extension"
        pageType="ProductPage"
      />

      {/* Hero */}
      <section className="relative overflow-hidden bg-muted/30 border-b border-border">
        <div className="relative max-w-6xl mx-auto px-4 py-24 sm:py-32">
          <div className="text-center">
            <Badge variant="secondary" className="mb-4">
              Free on Chrome Web Store
            </Badge>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              Verify Content Provenance{" "}
              <span className="text-primary">in Your Browser</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
              The Encypher Verify extension detects C2PA watermarks on any
              webpage. See who signed content, when, and whether it has been
              tampered with. Free to install, no account required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild>
                <a href={CHROME_STORE_URL} target="_blank" rel="noopener noreferrer">
                  Add to Chrome - Free
                  <ArrowRight className="ml-2 h-4 w-4" />
                </a>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="/auth/register">
                  Get a Free Signing Account
                </Link>
              </Button>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">
              Works on Chrome, Edge, and Brave. Verification is always free.
            </p>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 bg-background">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Verify in Three Steps</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              No configuration needed. Install and start verifying immediately.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step) => (
              <div key={step.n} className="text-center">
                <div className="w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  {step.n}
                </div>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-muted-foreground">{step.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Screenshots */}
      <section className="py-20 bg-background border-b border-border">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">See It in Action</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              A visitor sees the verification badge. They click. They see provenance details.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="rounded-xl border border-border overflow-hidden bg-muted/20">
              <Image
                src="/assets/screenshots/chrome-extension/screenshot-1-image-verification.png"
                alt="Encypher Chrome extension verifying an image with C2PA provenance"
                width={640}
                height={400}
                className="w-full h-auto"
              />
              <div className="p-4">
                <p className="text-sm font-medium">Image verification</p>
                <p className="text-xs text-muted-foreground mt-1">
                  The extension detects a signed image and shows provenance details.
                </p>
              </div>
            </div>
            <div className="rounded-xl border border-border overflow-hidden bg-muted/20">
              <Image
                src="/assets/screenshots/chrome-extension/screenshot-4-text-verification.png"
                alt="Encypher Chrome extension verifying signed text on a webpage"
                width={640}
                height={400}
                className="w-full h-auto"
              />
              <div className="p-4">
                <p className="text-sm font-medium">Text verification</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Signed text is detected automatically. Click the badge to see who signed it and when.
                </p>
              </div>
            </div>
            <div className="rounded-xl border border-border overflow-hidden bg-muted/20">
              <Image
                src="/assets/screenshots/chrome-extension/screenshot-2-context-menu.png"
                alt="Right-click context menu to verify selected text"
                width={640}
                height={400}
                className="w-full h-auto"
              />
              <div className="p-4">
                <p className="text-sm font-medium">Right-click to verify</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Select any text, right-click, and choose Verify to check provenance on demand.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-muted/30 border-y border-border">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">What the Extension Does</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Verify provenance anywhere on the web. Sign content when you have
              an account.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <Card key={f.title} className="border-2 hover:border-primary/50 transition-colors">
                <CardHeader>
                  <f.icon className="h-10 w-10 text-primary mb-2" />
                  <CardTitle className="text-xl">{f.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">{f.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Verification vs Signing */}
      <section className="py-20 bg-background">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Free to Verify. Simple to Sign.</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            <Card className="border-2 border-primary shadow-lg">
              <CardHeader className="text-center pb-2">
                <Badge className="w-fit mx-auto mb-2">No account needed</Badge>
                <CardTitle className="text-2xl">Verify</CardTitle>
                <div className="mt-2">
                  <span className="text-4xl font-bold">Free</span>
                </div>
                <CardDescription className="mt-2">
                  Verify provenance on any page, any time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  {[
                    "Detect C2PA watermarks on any page",
                    "See signer identity and timestamp",
                    "Tamper detection",
                    "Right-click to verify selected text",
                    "Auto-scan on page load",
                    "Unlimited verifications",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-sm">{item}</span>
                    </li>
                  ))}
                </ul>
                <Button className="w-full" asChild>
                  <a href={CHROME_STORE_URL} target="_blank" rel="noopener noreferrer">
                    Install Free Extension
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </a>
                </Button>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardHeader className="text-center pb-2">
                <Badge variant="secondary" className="w-fit mx-auto mb-2">Free account</Badge>
                <CardTitle className="text-2xl">Verify + Sign</CardTitle>
                <div className="mt-2">
                  <span className="text-4xl font-bold">Free</span>
                </div>
                <CardDescription className="mt-2">
                  Sign your own content from the browser
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  {[
                    "Everything in Verify",
                    "Sign selected text from the popup",
                    "1,000 signings per month",
                    "API key from Encypher dashboard",
                    "Your identity embedded in manifests",
                    "Upgrade for unlimited signing",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-sm">{item}</span>
                    </li>
                  ))}
                </ul>
                <Button className="w-full" variant="outline" asChild>
                  <Link href="/auth/register">
                    Create Free Account
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 bg-muted/30 border-y border-border">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            {faqs.map((faq) => (
              <div
                key={faq.q}
                className="bg-card border border-border rounded-lg p-6"
              >
                <h3 className="text-lg font-semibold mb-2">{faq.q}</h3>
                <p className="text-muted-foreground">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Start Verifying Content Today
          </h2>
          <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
            Free to install. No account required to verify. Works on Chrome,
            Edge, and Brave.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" asChild>
              <a href={CHROME_STORE_URL} target="_blank" rel="noopener noreferrer">
                Install from Chrome Web Store
                <ArrowRight className="ml-2 h-4 w-4" />
              </a>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="bg-transparent border-primary-foreground text-primary-foreground hover:bg-primary-foreground/10"
              asChild
            >
              <Link href="/tools/sign-verify">Try the Web Tool Instead</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Related tools */}
      <section className="py-12 bg-background border-t border-border">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <p className="text-sm text-muted-foreground mb-4">
            Prefer a web-based tool?
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <Link href="/tools/sign-verify" className="text-primary hover:underline font-medium">
              Sign / Verify Tool
            </Link>
            <span className="text-muted-foreground">-</span>
            <Link href="/tools/verify" className="text-primary hover:underline font-medium">
              Verify Only
            </Link>
            <span className="text-muted-foreground">-</span>
            <Link href="/tools/sign" className="text-primary hover:underline font-medium">
              Sign Only
            </Link>
            <span className="text-muted-foreground">-</span>
            <Link href="/tools" className="text-primary hover:underline font-medium">
              All Tools
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
