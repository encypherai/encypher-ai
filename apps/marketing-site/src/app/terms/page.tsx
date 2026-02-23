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
          <strong>Last Updated:</strong> February 23, 2026
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
          <p className="mb-4">
            By accessing or using Encypher&apos;s website, APIs, Chrome extension, dashboard, and related services (collectively, the &quot;Services&quot;), you agree to be bound by these Terms of Service (&quot;Terms&quot;). If you do not agree to these Terms, please do not use our Services.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">2. Description of Services</h2>
          <p className="mb-4">
            Encypher provides content authenticity, provenance verification, and licensing infrastructure for content publishers and AI companies. Our Services include:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Cryptographic text watermarking and C2PA-compliant content signing</li>
            <li>Content verification and provenance authentication (public API, no account required)</li>
            <li>Chrome extension for in-browser signing and verification (&quot;Encypher Verify&quot;)</li>
            <li>Attribution Analytics: web-surface detection of where signed content appears</li>
            <li>Formal Notice packages: cryptographically-backed notice to AI companies</li>
            <li>Evidence packages and enforcement bundles for legal proceedings</li>
            <li>Publisher Coalition program: content licensing and revenue-share program (see Section 7)</li>
            <li>Interactive demonstrations and technical documentation</li>
          </ul>
          <p className="mb-4">
            <strong>Free Tier</strong> includes full C2PA-compliant signing infrastructure, public verification, and Publisher Coalition membership. <strong>Enterprise Tier</strong> includes unlimited signing, sentence-level Merkle tree authentication, advanced analytics, and implementation services. Current pricing and tier details are available at encypherai.com/pricing.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">3. User Accounts and Registration</h2>
          <p className="mb-4">
            Some features require an account. You may create an account directly on our website or through the Chrome extension&apos;s optional onboarding flow, which provisions a free account and API key using your email address. You are responsible for:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Maintaining the confidentiality of your account credentials and API keys</li>
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
            <li>Sign content you do not own or are not authorized to sign on behalf of the rights holder</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">5. Intellectual Property</h2>
          <p className="mb-4">
            All content, features, and functionality of the Services, including but not limited to text, graphics, logos, software, and technology, are owned by Encypher or its licensors and are protected by intellectual property laws. Our cryptographic watermarking and sentence-level tracking methods are covered by pending patent applications.
          </p>
          <p className="mb-4">
            You may not copy, modify, distribute, sell, or lease any part of our Services without our express written permission.
          </p>
          <p className="mb-4">
            You retain all ownership rights in any content you sign using our Services. Signing your content with Encypher does not transfer any ownership rights to us, except as expressly described in Section 7 (Publisher Coalition Program).
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

          <h3 className="text-xl font-semibold mb-3 mt-6">6.1 Chrome Extension Data Collection</h3>
          <p className="mb-4">
            The Encypher Verify Chrome extension collects data as follows:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>
              <strong>Content Discovery Tracking:</strong> When the extension detects signed content on a page, it reports an anonymized discovery event to Encypher. This event includes the sanitized page URL and domain (query parameters and hash fragments removed), page title, signer information from the signature, verification result, and an ephemeral anonymous session ID that resets each browser session. This tracking does not include your name, email, browsing history, or any information that could identify you personally. It is a core product feature that allows content owners to monitor where their signed content appears on the web.
            </li>
            <li>
              <strong>Content Signing:</strong> When you sign content, the text you submit and your API key are sent to the Encypher API. Signed content metadata (document ID, signer ID, timestamp) may be stored for audit purposes.
            </li>
            <li>
              <strong>Content Verification:</strong> Only the specific signed text block is sent to the Encypher API for verification, never full page content. Verification results are cached locally in your browser for 1 hour.
            </li>
            <li>
              <strong>Local Storage:</strong> Your API key, extension settings, and temporary verification cache are stored locally in Chrome&apos;s secure storage. API keys are never transmitted to third parties.
            </li>
          </ul>
          <p className="mb-4">
            A full description of Chrome extension data practices is available in the extension&apos;s privacy policy, accessible from the Chrome Web Store listing and from the extension settings page.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">6.2 Signed Content Metadata</h3>
          <p className="mb-4">
            When you sign content using any Encypher tool (API, Chrome extension, WordPress plugin, or CLI), we store the following metadata on our servers: document ID, signer ID, timestamp, signing configuration, and a content fingerprint. This metadata enables verification, audit trails, and (where applicable) Coalition licensing. We do not store the full text of signed content on our servers.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">7. Publisher Coalition Program</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.1 Enrollment</h3>
          <p className="mb-4">
            All Encypher accounts are enrolled in the Publisher Coalition (&quot;Coalition&quot;) by default. Enrollment is managed as an organization-level setting: when Coalition is enabled for your organization, all content you mark using Encypher&apos;s tools is included in the Coalition catalog. You may disable Coalition enrollment at any time through your account settings, which removes your organization and all its marked content from the Coalition prospectively.
          </p>
          <p className="mb-4">
            Coalition enrollment requires that the account holder or authorized representative be at least 18 years of age (or the age of majority in their jurisdiction, whichever is greater) and have authority to grant the license described in Section 7.2 on behalf of their organization.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.2 What Coalition Membership Means</h3>
          <p className="mb-4">
            The Coalition is a verified catalog of cryptographically-signed, provenance-stamped content. Encypher uses the Coalition to negotiate licensing agreements with AI companies, news aggregators, research institutions, and other content licensees on behalf of enrolled publishers. The goal is to create licensing revenue from content that would otherwise generate no revenue at all.
          </p>
          <p className="mb-4">
            By enrolling, you grant Encypher a <strong>non-exclusive, worldwide, sublicensable</strong> (solely to approved Coalition licensees) license to:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Include your enrolled content in the Coalition catalog</li>
            <li>Display metadata about your content (title, author name, signing date, provenance data) to potential licensees</li>
            <li>Sublicense your content to approved licensees for their permitted uses, which may include AI model training, search indexing, research, and content distribution</li>
            <li>Reproduce and distribute your content as reasonably necessary to fulfill those sublicenses</li>
          </ul>
          <p className="mb-4">
            <strong>This license is non-exclusive.</strong> You retain all ownership rights and may continue to publish, license, sell, or distribute your content through any other channel without restriction.
          </p>
          <p className="mb-4">
            <strong>AI Training Disclosure:</strong> Approved Coalition licensees may include AI companies that license content for model training purposes. By enrolling in the Coalition, you acknowledge and consent to this potential use. If you do not want your content licensed for AI training, do not enroll in the Coalition.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.3 Enrolled Content</h3>
          <p className="mb-4">
            &quot;Enrolled Content&quot; means all content signed using Encypher&apos;s tools by your organization while Coalition enrollment is enabled. Content signed before your enrollment date, or signed while Coalition was disabled, is not included. If you re-enable Coalition after a period of disablement, only content signed from that point forward is enrolled.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.4 Revenue Share</h3>
          <p className="mb-4">
            Encypher shares licensing revenue with enrolled publishers. Revenue share rates and payment terms are specified in the Publisher Coalition Agreement applicable to your account. Two tracks apply:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>
              <strong>Coalition Deals:</strong> Where Encypher sources and negotiates the licensing agreement on your behalf using collective coalition leverage, you receive a majority share of Net Revenue and Encypher retains the remainder as specified in your agreement.
            </li>
            <li>
              <strong>Self-Service Deals:</strong> Where you negotiate a licensing agreement directly with a licensee and use Encypher&apos;s infrastructure to fulfill it, you retain a larger share of Net Revenue. You may choose the applicable track on a per-deal basis.
            </li>
          </ul>
          <p className="mb-4">
            In all cases, any licensing revenue generated using Encypher&apos;s infrastructure is subject to a revenue share with Encypher as described in your account agreement.
          </p>
          <p className="mb-4">
            &quot;Net Revenue&quot; means gross payments received by Encypher from licensees for Coalition content, less payment processing fees, applicable taxes, and third-party platform transaction fees. Encypher will not deduct its internal operating costs or personnel costs from Net Revenue.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.5 Licensing Program</h3>
          <p className="mb-4">
            Encypher is actively developing the licensing infrastructure through which Coalition content is made available to licensees and revenue share payments are distributed to publishers. Encypher will notify enrolled publishers by email as licensing program milestones are reached.
          </p>
          <p className="mb-4">
            Once licensing deals are active, payments will be calculated on a periodic basis and distributed to enrolled publishers according to the terms of the Publisher Coalition Agreement. Encypher will provide account-level reporting through your dashboard showing licensing activity and payment calculations.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.6 Withdrawal from the Coalition</h3>
          <p className="mb-4">
            You may withdraw from the Coalition at any time through your account settings. Withdrawal is effective immediately for new content: no content signed after withdrawal will be included in the Coalition.
          </p>
          <p className="mb-4">
            For content already sublicensed to a licensee before your withdrawal date, a <strong>90-day wind-down period</strong> applies. During this period, existing sublicenses may continue, and you will receive your revenue share for any use of your content during the wind-down. After the wind-down period, Encypher will not renew or extend any sublicense for your withdrawn content.
          </p>
          <p className="mb-4">
            Withdrawal does not affect your access to Encypher&apos;s signing and verification tools. You may re-enroll at any time, but re-enrollment applies prospectively only.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.7 Content Warranties for Coalition Enrollment</h3>
          <p className="mb-4">
            By enrolling content in the Coalition, you represent and warrant that:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>You are the original author or creator of the content, or you have obtained written authorization from the rights holder to include it in the Coalition</li>
            <li>If you created the content in the course of employment, you have obtained your employer&apos;s written authorization to enroll it</li>
            <li>The content does not infringe any third party&apos;s copyright, trademark, privacy, publicity, or other intellectual property rights</li>
            <li>The content is not defamatory, fraudulent, obscene, or otherwise in violation of applicable law</li>
          </ul>
          <p className="mb-4">
            Encypher reserves the right to remove any content from the Coalition that violates these standards, with notice to you. If Encypher receives a third-party claim asserting rights over your enrolled content, Encypher may temporarily remove the disputed content pending resolution, without affecting your account or other enrolled content.
          </p>
          <p className="mb-4">
            You agree to indemnify and hold harmless Encypher and its approved licensees from claims, damages, losses, or expenses arising from your breach of these content warranties.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">8. Third-Party Services</h2>
          <p className="mb-4">
            Our Services may contain links to or integrate with third-party services. We are not responsible for the content, privacy policies, or practices of third-party services. Notable integrations include:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li><strong>Chrome Web Store:</strong> The Encypher Verify extension is distributed through Google&apos;s Chrome Web Store, subject to Google&apos;s terms and policies</li>
            <li><strong>WordPress/Automattic:</strong> Our WordPress plugin is distributed through the WordPress plugin ecosystem</li>
            <li><strong>Payment processors:</strong> Coalition revenue share payments are processed through third-party payment platforms (ACH/wire, PayPal, or similar) subject to their own terms</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">9. Disclaimers and Limitation of Liability</h2>
          <p className="mb-4">
            THE SERVICES ARE PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED. TO THE FULLEST EXTENT PERMITTED BY LAW, ENCYPHER DISCLAIMS ALL WARRANTIES, INCLUDING BUT NOT LIMITED TO MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
          </p>
          <p className="mb-4">
            IN NO EVENT SHALL ENCYPHER BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR RELATED TO YOUR USE OF THE SERVICES.
          </p>
          <p className="mb-4">
            Encypher does not guarantee that signing your content will result in any particular legal outcome, licensing revenue, or enforcement result. The willful infringement framework described in our marketing materials reflects our understanding of applicable law but is not legal advice. We recommend consulting qualified legal counsel regarding your specific situation.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">10. Indemnification</h2>
          <p className="mb-4">
            You agree to indemnify and hold harmless Encypher, its officers, directors, employees, and agents from any claims, damages, losses, liabilities, and expenses arising out of your use of the Services, your violation of these Terms, or your enrollment of content in the Coalition that infringes third-party rights.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">11. Modifications to Terms</h2>
          <p className="mb-4">
            We reserve the right to modify these Terms at any time. We will notify users of material changes by posting the updated Terms on our website with a new &quot;Last Updated&quot; date. For material changes to Section 7 (Publisher Coalition Program), we will provide at least 30 days notice by email to enrolled Coalition members before the changes take effect. Your continued use of the Services after such changes constitutes acceptance of the modified Terms.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">12. Termination</h2>
          <p className="mb-4">
            We may terminate or suspend your access to the Services at any time, without prior notice or liability, for any reason, including if you breach these Terms. Upon termination, Coalition membership and any associated license grants terminate subject to the wind-down provisions in Section 7.6. Any revenue share accrued before termination for cause will be paid according to the standard payment schedule.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">13. Governing Law</h2>
          <p className="mb-4">
            These Terms shall be governed by and construed in accordance with the laws of the United States, without regard to its conflict of law provisions.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">14. Contact Information</h2>
          <p className="mb-4">
            If you have any questions about these Terms, please contact us at:
          </p>
          <p className="mb-4">
            <strong>Encypher</strong><br />
            Legal: legal@encypherai.com<br />
            Privacy: privacy@encypherai.com<br />
            Support: support@encypherai.com
          </p>
        </section>
      </div>
    </div>
  );
}
