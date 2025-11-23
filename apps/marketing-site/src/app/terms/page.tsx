import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Terms of Service | Encypher',
  description: 'Terms of Service for Encypher - Content authenticity and provenance solutions.',
  robots: 'noindex, nofollow',
};

export default function TermsPage() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl">
      <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
      <div className="prose prose-slate dark:prose-invert max-w-none">
        <p className="text-muted-foreground mb-8">
          <strong>Last Updated:</strong> {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
          <p className="mb-4">
            By accessing or using Encypher's website, services, and demos (collectively, the "Services"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, please do not use our Services.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">2. Description of Services</h2>
          <p className="mb-4">
            Encypher provides content authenticity, provenance verification, and performance analytics solutions for AI companies and content publishers. Our Services include:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Cryptographic watermarking and content authentication</li>
            <li>Performance intelligence and analytics for AI models</li>
            <li>Content protection and licensing solutions for publishers</li>
            <li>Interactive demonstrations and technical documentation</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">3. User Accounts and Registration</h2>
          <p className="mb-4">
            Some features of our Services may require you to create an account. You are responsible for:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Maintaining the confidentiality of your account credentials</li>
            <li>All activities that occur under your account</li>
            <li>Providing accurate and current information</li>
            <li>Notifying us immediately of any unauthorized use of your account</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">4. Acceptable Use</h2>
          <p className="mb-4">
            You agree not to:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Use the Services for any illegal or unauthorized purpose</li>
            <li>Attempt to gain unauthorized access to our systems or networks</li>
            <li>Interfere with or disrupt the Services or servers</li>
            <li>Transmit any viruses, malware, or harmful code</li>
            <li>Reverse engineer, decompile, or disassemble any part of the Services</li>
            <li>Use the Services to infringe on intellectual property rights</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">5. Intellectual Property</h2>
          <p className="mb-4">
            All content, features, and functionality of the Services, including but not limited to text, graphics, logos, software, and technology, are owned by Encypher or its licensors and are protected by intellectual property laws.
          </p>
          <p className="mb-4">
            You may not copy, modify, distribute, sell, or lease any part of our Services without our express written permission.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">6. User Data and Privacy</h2>
          <p className="mb-4">
            We are committed to protecting your privacy. Our collection and use of personal information is governed by our Privacy Policy. By using our Services, you consent to our data practices as described in the Privacy Policy.
          </p>
          <p className="mb-4">
            <strong>We will never sell your personal data to third parties.</strong> We collect and use data solely for:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Providing and improving our Services</li>
            <li>Analytics to optimize website and demo performance</li>
            <li>Communicating with you about our Services</li>
            <li>Complying with legal obligations</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">7. Third-Party Services</h2>
          <p className="mb-4">
            Our Services may contain links to third-party websites or services, including Google Colab for technical demonstrations. We are not responsible for the content, privacy policies, or practices of third-party services.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">8. Disclaimers and Limitation of Liability</h2>
          <p className="mb-4">
            THE SERVICES ARE PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED. TO THE FULLEST EXTENT PERMITTED BY LAW, ENCYPHER DISCLAIMS ALL WARRANTIES, INCLUDING BUT NOT LIMITED TO MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
          </p>
          <p className="mb-4">
            IN NO EVENT SHALL ENCYPHER BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR RELATED TO YOUR USE OF THE SERVICES.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">9. Indemnification</h2>
          <p className="mb-4">
            You agree to indemnify and hold harmless Encypher, its officers, directors, employees, and agents from any claims, damages, losses, liabilities, and expenses arising out of your use of the Services or violation of these Terms.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">10. Modifications to Terms</h2>
          <p className="mb-4">
            We reserve the right to modify these Terms at any time. We will notify users of material changes by posting the updated Terms on our website with a new "Last Updated" date. Your continued use of the Services after such changes constitutes acceptance of the modified Terms.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">11. Termination</h2>
          <p className="mb-4">
            We may terminate or suspend your access to the Services at any time, without prior notice or liability, for any reason, including if you breach these Terms.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">12. Governing Law</h2>
          <p className="mb-4">
            These Terms shall be governed by and construed in accordance with the laws of the United States, without regard to its conflict of law provisions.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">13. Contact Information</h2>
          <p className="mb-4">
            If you have any questions about these Terms, please contact us at:
          </p>
          <p className="mb-4">
            <strong>Encypher</strong><br />
            Email: legal@encypherai.com
          </p>
        </section>
      </div>
    </div>
  );
}
