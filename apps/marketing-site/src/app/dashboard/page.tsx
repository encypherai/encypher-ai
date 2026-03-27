/**
 * Dashboard Redirect Page
 *
 * This page redirects authenticated users to the actual dashboard at dashboard.encypher.com.
 * The marketing site should not have its own dashboard - all dashboard functionality
 * lives at the dashboard subdomain.
 */
"use client";
import { useEffect } from "react";
import { RefreshCw } from "lucide-react";

export default function DashboardPage() {

  useEffect(() => {
    // Redirect to the actual dashboard
    const dashboardUrl = process.env.NEXT_PUBLIC_DASHBOARD_URL || "https://dashboard.encypher.com";
    window.location.href = dashboardUrl;
  }, []);

  // Show loading while redirecting
  return (
    <div className="flex flex-col justify-center items-center h-screen">
      <div className="animate-spin mb-4">
        <RefreshCw className="h-8 w-8 text-primary" />
      </div>
      <p className="text-lg">Redirecting to dashboard...</p>
    </div>
  );
}
