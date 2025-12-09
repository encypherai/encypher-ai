import { redirect } from 'next/navigation';

/**
 * Licensing page redirects to pricing page.
 * /pricing is the canonical URL for SEO purposes.
 * This redirect preserves old links.
 */
export default function LicensingPage() {
  redirect('/pricing');
}
