import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent } from '@encypher/design-system';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <Navigation />
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-delft-blue to-blue-ncs text-white py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center space-y-6">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight">
              Cryptographic Content
              <br />
              <span className="text-columbia-blue">Authentication</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-columbia-blue/90 max-w-3xl mx-auto">
              Enterprise-grade content verification powered by cryptographic signatures.
              Protect your content, prove authenticity, build trust.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
              {/* High-contrast CTA - Columbia Blue */}
              <Link href="/signup">
                <Button variant="primary" size="xl">
                  Get Started Free
                </Button>
              </Link>
              
              <Link href="/demo">
                <Button variant="outline" size="xl" className="border-white text-white hover:bg-white hover:text-delft-blue">
                  View Demo
                </Button>
              </Link>
            </div>
            
            <p className="text-sm text-columbia-blue/70 pt-4">
              Free tier: 1,000 signatures/month • No credit card required
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-white">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-delft-blue mb-4">
              Why Encypher?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Built for publishers, newsrooms, and content creators who demand authenticity
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card variant="elevated" padding="lg">
              <CardHeader>
                <div className="w-12 h-12 bg-columbia-blue rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <CardTitle>Cryptographic Security</CardTitle>
                <CardDescription>
                  Military-grade cryptographic signatures ensure your content cannot be tampered with
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card variant="elevated" padding="lg">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-ncs rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <CardTitle>Lightning Fast</CardTitle>
                <CardDescription>
                  Sign and verify content in milliseconds. Built for scale with enterprise performance
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card variant="elevated" padding="lg">
              <CardHeader>
                <div className="w-12 h-12 bg-rosy-brown rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <CardTitle>Easy Integration</CardTitle>
                <CardDescription>
                  Python SDK, REST API, and CLI tools. Integrate in minutes, not weeks
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-br from-columbia-blue to-blue-ncs text-white">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Protect Your Content?
          </h2>
          <p className="text-xl mb-8 text-white/90">
            Join thousands of publishers using Encypher to authenticate their content
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup">
              <Button variant="primary" size="xl" className="bg-white text-blue-ncs hover:bg-white/90">
                Start Free Trial
              </Button>
            </Link>
            
            <Link href="/pricing">
              <Button variant="outline" size="xl" className="border-white text-white hover:bg-white hover:text-blue-ncs">
                View Pricing
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-delft-blue text-white py-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-bold text-lg mb-4">Encypher</h3>
              <p className="text-columbia-blue/70 text-sm">
                Cryptographic content authentication for the modern web
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-columbia-blue/70">
                <li><Link href="/features" className="hover:text-columbia-blue">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-columbia-blue">Pricing</Link></li>
                <li><Link href="/docs" className="hover:text-columbia-blue">Documentation</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-columbia-blue/70">
                <li><Link href="/about" className="hover:text-columbia-blue">About</Link></li>
                <li><Link href="/blog" className="hover:text-columbia-blue">Blog</Link></li>
                <li><Link href="/contact" className="hover:text-columbia-blue">Contact</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-columbia-blue/70">
                <li><Link href="/privacy" className="hover:text-columbia-blue">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-columbia-blue">Terms</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-columbia-blue/20 mt-8 pt-8 text-center text-sm text-columbia-blue/70">
            <p>&copy; 2025 Encypher. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  );
}
