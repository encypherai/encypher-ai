import React from "react";
import { Metadata } from "next";
import { getSiteUrl } from "@/lib/env";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Shield, Zap, Users, FileText, BarChart3, Lock, Globe, ArrowRight, Download } from "lucide-react";
import AISummary from "@/components/seo/AISummary";

export const metadata: Metadata = {
  title: "Encypher Provenance - WordPress Plugin for C2PA Content Authentication",
  description: "Protect your WordPress content with cryptographic proof of authorship. C2PA-compliant digital signatures prove when content was created, by whom, and detect tampering. Fight misinformation, plagiarism, and AI-generated content theft.",
  keywords: [
    "wordpress plugin",
    "c2pa wordpress",
    "content authenticity wordpress",
    "wordpress content verification",
    "wordpress plagiarism protection",
    "wordpress digital signature",
    "wordpress content protection",
    "ai content detection wordpress",
    "wordpress misinformation",
    "wordpress proof of authorship",
    "content provenance wordpress",
    "wordpress copyright protection",
    "wordpress anti-plagiarism",
    "c2pa plugin",
    "content authentication plugin",
  ],
  openGraph: {
    title: "Encypher Provenance - WordPress Plugin for C2PA Content Authentication",
    description: "Protect your WordPress content with cryptographic proof of authorship. C2PA-compliant digital signatures prove when content was created, by whom, and detect tampering.",
    url: "https://encypherai.com/tools/wordpress",
    siteName: "Encypher",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Encypher Provenance - WordPress Plugin",
    description: "C2PA content authentication for WordPress. Protect your posts with cryptographic proof of authorship.",
  },
  metadataBase: new URL(getSiteUrl()),
};

const features = [
  {
    icon: Shield,
    title: "C2PA Compliant",
    description: "Built on the same standards used by Google, BBC, Adobe, Microsoft, and OpenAI.",
  },
  {
    icon: Zap,
    title: "Auto-Sign on Publish",
    description: "Content is automatically signed when you publish or update posts.",
  },
  {
    icon: Lock,
    title: "Tamper Detection",
    description: "Cryptographic signatures detect if content has been modified after signing.",
  },
  {
    icon: FileText,
    title: "Sentence-Level Attribution",
    description: "Track provenance at the sentence level for quote verification (Pro+).",
  },
  {
    icon: Users,
    title: "Coalition Membership",
    description: "Join the Encypher Coalition for content licensing revenue sharing.",
  },
  {
    icon: BarChart3,
    title: "Analytics Dashboard",
    description: "Track signing coverage, verification hits, and content protection status.",
  },
];

const tiers = [
  {
    name: "Starter",
    price: "Free",
    description: "Perfect for bloggers and small publishers",
    features: [
      "Auto-sign on publish/update",
      "Document-level C2PA manifests",
      "Public verification badge",
      "Coalition membership (65/35 split)",
      "100 posts per bulk operation",
    ],
    cta: "Get Started Free",
    highlighted: false,
  },
  {
    name: "Professional",
    price: "$99/mo",
    description: "For serious publishers and newsrooms",
    features: [
      "Everything in Starter",
      "Sentence-level attribution",
      "Merkle tree encoding",
      "BYOK (Bring Your Own Key)",
      "Coalition membership (70/30 split)",
      "Unlimited bulk signing",
      "Priority support",
    ],
    cta: "Start Pro Trial",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For large organizations and media companies",
    features: [
      "Everything in Professional",
      "Custom branding (white-label)",
      "SSO integration",
      "Dedicated account manager",
      "Coalition membership (80/20 split)",
      "SLA guarantee",
      "On-premise deployment option",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
];

const partners = [
  "Google", "BBC", "Adobe", "Microsoft", "OpenAI", "New York Times", "Associated Press"
];

export default function WordPressPage() {
  return (
    <main className="min-h-screen">
      <AISummary
        title="Encypher Provenance - WordPress Plugin for C2PA Content Authentication"
        whatWeDo="WordPress plugin that embeds invisible C2PA-compliant cryptographic signatures into blog posts. Proves authorship, detects tampering, and fights misinformation with verifiable content authenticity."
        whoItsFor="WordPress publishers, bloggers, newsrooms, and content creators who want to protect their content from plagiarism, misattribution, and AI-generated content theft."
        keyDifferentiator="Built on C2PA standards co-authored with Google, BBC, Adobe, Microsoft, and OpenAI. Same technology used by major news organizations. Invisible embeddings that survive copy-paste."
        primaryValue="Free tier available. Auto-signs content on publish. Public verification badge lets readers verify authenticity. Coalition membership for content licensing revenue."
        pagePath="/tools/wordpress"
        pageType="SoftwareApplication"
      />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
        <div className="relative max-w-6xl mx-auto px-4 py-24 sm:py-32">
          <div className="text-center">
            <Badge variant="secondary" className="mb-4 bg-blue-500/20 text-blue-300 border-blue-500/30">
              C2PA Compliant
            </Badge>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              Protect Your WordPress Content with{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                Cryptographic Proof
              </span>
            </h1>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-8">
              Embed invisible digital signatures that prove when your content was created, by whom, 
              and whether it&apos;s been tampered with. Fight misinformation, plagiarism, and content theft.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white" asChild>
                <Link href="https://dashboard.encypherai.com" target="_blank">
                  <Download className="mr-2 h-5 w-5" />
                  Get Free API Key
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="border-slate-500 bg-slate-700/50 text-white hover:bg-slate-700" asChild>
                <Link href="/pricing">
                  View Pricing
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Bar */}
      <section className="bg-slate-100 dark:bg-slate-800 py-8 border-y">
        <div className="max-w-6xl mx-auto px-4">
          <p className="text-center text-sm text-muted-foreground mb-4">
            Built on C2PA standards developed with industry leaders
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            {partners.map((partner) => (
              <span key={partner} className="text-lg font-semibold text-slate-600 dark:text-slate-400">
                {partner}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 bg-background">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Everything You Need to Protect Your Content</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Encypher Provenance integrates seamlessly with WordPress to provide enterprise-grade 
              content authentication without changing your workflow.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <Card key={feature.title} className="border-2 hover:border-blue-500/50 transition-colors">
                <CardHeader>
                  <feature.icon className="h-10 w-10 text-blue-600 mb-2" />
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-slate-50 dark:bg-slate-900">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">How It Works</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Three simple steps to protect your WordPress content
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2">Install & Configure</h3>
              <p className="text-muted-foreground">
                Install the plugin and add your free API key from the Encypher dashboard.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">Write & Publish</h3>
              <p className="text-muted-foreground">
                Write your content as usual. The plugin automatically signs it when you publish.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Readers Verify</h3>
              <p className="text-muted-foreground">
                A verification badge lets readers confirm your content is authentic and untampered.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 bg-background">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Simple, Transparent Pricing</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Start free and upgrade as you grow. All plans include core C2PA signing.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {tiers.map((tier) => (
              <Card 
                key={tier.name} 
                className={`relative ${tier.highlighted ? 'border-blue-500 border-2 shadow-lg' : ''}`}
              >
                {tier.highlighted && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600">
                    Most Popular
                  </Badge>
                )}
                <CardHeader className="text-center pb-2">
                  <CardTitle className="text-2xl">{tier.name}</CardTitle>
                  <div className="mt-2">
                    <span className="text-4xl font-bold">{tier.price}</span>
                    {tier.price !== "Free" && tier.price !== "Custom" && (
                      <span className="text-muted-foreground">/month</span>
                    )}
                  </div>
                  <CardDescription className="mt-2">{tier.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {tier.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2">
                        <CheckCircle className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button 
                    className={`w-full ${tier.highlighted ? 'bg-blue-600 hover:bg-blue-700' : ''}`}
                    variant={tier.highlighted ? 'default' : 'outline'}
                    asChild
                  >
                    <Link href="https://dashboard.encypherai.com">
                      {tier.cta}
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-20 bg-slate-50 dark:bg-slate-900">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Who Uses Encypher Provenance?</h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">News Publishers</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Prove article authenticity and combat misinformation with verifiable provenance.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Bloggers</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Protect original content from plagiarism and prove you published first.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Legal & Finance</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Create tamper-evident records for compliance and audit trails.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">AI Companies</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Respect content licensing through Coalition membership and rights metadata.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-cyan-600 text-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <Globe className="h-16 w-16 mx-auto mb-6 opacity-80" />
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Ready to Protect Your Content?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of publishers using C2PA standards to prove content authenticity. 
            Get started in minutes with our free tier.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" asChild>
              <Link href="https://dashboard.encypherai.com">
                Get Your Free API Key
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="bg-transparent border-white text-white hover:bg-white/10" asChild>
              <Link href="/pricing">
                View Full Pricing
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-background">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">What is C2PA?</h3>
              <p className="text-muted-foreground">
                C2PA (Coalition for Content Provenance and Authenticity) is an open standard for content 
                authentication developed by Adobe, Microsoft, Google, BBC, and others. It provides a way 
                to cryptographically sign content to prove its origin and detect tampering.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Are the signatures visible?</h3>
              <p className="text-muted-foreground">
                No. C2PA manifests are embedded using invisible Unicode variation selectors. They don&apos;t 
                affect how your content looks but can be extracted for verification.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Does this work with Gutenberg and Classic Editor?</h3>
              <p className="text-muted-foreground">
                Yes! The plugin supports both the block editor (Gutenberg) with a dedicated sidebar panel, 
                and the Classic Editor with a meta box.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">What happens when I edit a signed post?</h3>
              <p className="text-muted-foreground">
                The plugin automatically re-signs the content with a &quot;c2pa.edited&quot; action and maintains 
                a provenance chain linking to the previous version, creating a complete edit history.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Is my content sent to external servers?</h3>
              <p className="text-muted-foreground">
                Content is sent to Encypher&apos;s API for signing. We create cryptographic signatures but do 
                not store your full content. See our privacy policy for details.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
