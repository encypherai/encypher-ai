import { redirect } from 'next/navigation';

/**
 * Pricing page redirects to licensing page.
 * The licensing page contains our full pricing and tier information.
 */
export default function PricingPage() {
  redirect('/licensing');
}
