import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Privacy Policy | Encypher',
  description: 'Privacy Policy for Encypher - Learn how we protect and handle your data.',
  robots: 'noindex, nofollow',
};

export default function PrivacyPage() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl">
      <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
      <div className="prose prose-slate dark:prose-invert max-w-none">
        <p className="text-muted-foreground mb-8">
          <strong>Last Updated:</strong> {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">1. Introduction</h2>
          <p className="mb-4">
            Encypher ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website, services, and demos (collectively, the "Services").
          </p>
          <p className="mb-4">
            <strong className="text-primary">We will never sell your personal data to third parties.</strong> Your trust is paramount to us, and we are committed to transparent and responsible data practices.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">2. Information We Collect</h2>
          
          <h3 className="text-xl font-semibold mb-3 mt-6">2.1 Information You Provide</h3>
          <p className="mb-4">
            We may collect information that you voluntarily provide when you:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Create an account or register for our Services</li>
            <li>Contact us through forms or email</li>
            <li>Subscribe to newsletters or updates</li>
            <li>Participate in surveys or provide feedback</li>
            <li>Use our interactive demos</li>
          </ul>
          <p className="mb-4">
            This information may include: name, email address, company name, job title, and any other information you choose to provide.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">2.2 Automatically Collected Information</h3>
          <p className="mb-4">
            When you access our Services, we automatically collect certain information, including:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li><strong>Usage Data:</strong> Pages visited, time spent, click patterns, and navigation paths</li>
            <li><strong>Device Information:</strong> Browser type, operating system, device type, and screen resolution</li>
            <li><strong>Log Data:</strong> IP address, access times, and referring URLs</li>
            <li><strong>Cookies and Tracking Technologies:</strong> See Section 4 for details</li>
          </ul>

          <h3 className="text-xl font-semibold mb-3 mt-6">2.3 Demo Interaction Data</h3>
          <p className="mb-4">
            When you use our interactive demos, we may collect:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Demo completion rates and section interactions</li>
            <li>Time spent on each demo section</li>
            <li>User inputs and selections within demos (anonymized)</li>
            <li>Technical performance metrics</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">3. How We Use Your Information</h2>
          <p className="mb-4">
            We use the collected information for the following purposes:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li><strong>Service Delivery:</strong> To provide, maintain, and improve our Services</li>
            <li><strong>Analytics and Optimization:</strong> To analyze usage patterns and optimize website and demo performance</li>
            <li><strong>Communication:</strong> To respond to inquiries, send updates, and provide customer support</li>
            <li><strong>Personalization:</strong> To customize your experience and provide relevant content</li>
            <li><strong>Security:</strong> To detect, prevent, and address technical issues and security threats</li>
            <li><strong>Legal Compliance:</strong> To comply with legal obligations and protect our rights</li>
            <li><strong>Research and Development:</strong> To improve our technology and develop new features</li>
          </ul>
          <p className="mb-4 text-primary font-semibold">
            We will never sell your personal data to third parties or use it for purposes unrelated to providing and improving our Services.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">4. Cookies and Tracking Technologies</h2>
          <p className="mb-4">
            We use cookies and similar tracking technologies to enhance your experience and collect usage data. Types of cookies we use:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li><strong>Essential Cookies:</strong> Required for the Services to function properly</li>
            <li><strong>Analytics Cookies:</strong> Help us understand how visitors interact with our Services (e.g., Google Analytics)</li>
            <li><strong>Functional Cookies:</strong> Remember your preferences and settings</li>
            <li><strong>Performance Cookies:</strong> Collect information about how you use our Services to improve performance</li>
          </ul>
          <p className="mb-4">
            You can control cookies through your browser settings. Note that disabling certain cookies may limit your ability to use some features of our Services.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">5. Data Sharing and Disclosure</h2>
          <p className="mb-4">
            We do not sell your personal data. We may share your information only in the following circumstances:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li><strong>Service Providers:</strong> With trusted third-party vendors who assist in operating our Services (e.g., hosting, analytics, email services). These providers are contractually obligated to protect your data.</li>
            <li><strong>Legal Requirements:</strong> When required by law, court order, or governmental authority</li>
            <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets, with appropriate safeguards for your data</li>
            <li><strong>Protection of Rights:</strong> To protect our rights, property, or safety, or that of our users or the public</li>
            <li><strong>With Your Consent:</strong> When you explicitly authorize us to share your information</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">6. Third-Party Services</h2>
          <p className="mb-4">
            Our Services may integrate with or link to third-party services, including:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li><strong>Google Colab:</strong> For technical demonstrations</li>
            <li><strong>Analytics Providers:</strong> For website and demo performance tracking</li>
            <li><strong>Communication Tools:</strong> For customer support and engagement</li>
          </ul>
          <p className="mb-4">
            These third parties have their own privacy policies. We are not responsible for their data practices and encourage you to review their policies.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">7. Data Security</h2>
          <p className="mb-4">
            We implement appropriate technical and organizational measures to protect your personal information, including:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Encryption of data in transit and at rest</li>
            <li>Regular security assessments and updates</li>
            <li>Access controls and authentication mechanisms</li>
            <li>Employee training on data protection</li>
          </ul>
          <p className="mb-4">
            However, no method of transmission over the internet or electronic storage is 100% secure. While we strive to protect your data, we cannot guarantee absolute security.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">8. Data Retention</h2>
          <p className="mb-4">
            We retain your personal information only for as long as necessary to fulfill the purposes outlined in this Privacy Policy, unless a longer retention period is required or permitted by law. When data is no longer needed, we securely delete or anonymize it.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">9. Your Rights and Choices</h2>
          <p className="mb-4">
            Depending on your location, you may have the following rights regarding your personal information:
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li><strong>Access:</strong> Request a copy of the personal information we hold about you</li>
            <li><strong>Correction:</strong> Request correction of inaccurate or incomplete information</li>
            <li><strong>Deletion:</strong> Request deletion of your personal information</li>
            <li><strong>Objection:</strong> Object to certain processing of your information</li>
            <li><strong>Portability:</strong> Request transfer of your data to another service</li>
            <li><strong>Withdraw Consent:</strong> Withdraw consent for data processing where consent was the basis</li>
            <li><strong>Opt-Out:</strong> Unsubscribe from marketing communications</li>
          </ul>
          <p className="mb-4">
            To exercise these rights, please contact us at privacy@encypherai.com.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">10. Children's Privacy</h2>
          <p className="mb-4">
            Our Services are not intended for children under the age of 13 (or the applicable age of consent in your jurisdiction). We do not knowingly collect personal information from children. If you believe we have collected information from a child, please contact us immediately.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">11. International Data Transfers</h2>
          <p className="mb-4">
            Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place to protect your data in accordance with this Privacy Policy and applicable laws.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">12. Changes to This Privacy Policy</h2>
          <p className="mb-4">
            We may update this Privacy Policy from time to time. We will notify you of material changes by posting the updated policy on our website with a new "Last Updated" date. We encourage you to review this policy periodically.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">13. Contact Us</h2>
          <p className="mb-4">
            If you have questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:
          </p>
          <p className="mb-4">
            <strong>Encypher</strong><br />
            Email: contact@encypherai.com
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">14. California Privacy Rights (CCPA)</h2>
          <p className="mb-4">
            If you are a California resident, you have additional rights under the California Consumer Privacy Act (CCPA):
          </p>
          <ul className="list-disc ml-6 mb-4 space-y-2">
            <li>Right to know what personal information is collected, used, shared, or sold</li>
            <li>Right to delete personal information</li>
            <li>Right to opt-out of the sale of personal information (we do not sell personal information)</li>
            <li>Right to non-discrimination for exercising your privacy rights</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">15. European Privacy Rights (GDPR)</h2>
          <p className="mb-4">
            If you are located in the European Economic Area (EEA), you have rights under the General Data Protection Regulation (GDPR), including those outlined in Section 9. We process your data based on legitimate interests, contractual necessity, or your consent.
          </p>
        </section>
      </div>
    </div>
  );
}
