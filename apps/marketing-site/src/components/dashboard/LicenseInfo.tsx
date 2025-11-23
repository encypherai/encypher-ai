"use client";
import React from "react";
import { BadgeInfo, ShieldCheck, AlertTriangle, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export type LicenseInfoProps = {
  licenseKey: string;
  tier: string;
  status: string;
  issuedAt: string;
  expiresAt: string;
  isTrial: boolean;
};

// Helper to map backend License to LicenseInfoProps
export function mapLicenseToProps(license: {
  license_key: string;
  tier: string;
  status: string;
  issued_at: string;
  expires_at: string;
  is_trial: boolean;
}): LicenseInfoProps {
  return {
    licenseKey: license.license_key,
    tier: license.tier,
    status: license.status,
    issuedAt: license.issued_at,
    expiresAt: license.expires_at,
    isTrial: license.is_trial,
  };
}

// Utility: Capitalize each word for tier display
function normalizeTier(tier: string) {
  return tier
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export const LicenseInfo: React.FC<LicenseInfoProps> = ({
  licenseKey,
  tier,
  status,
  issuedAt,
  expiresAt,
  isTrial,
}) => {
  const now = new Date();
  const exp = new Date(expiresAt);
  const msInDay = 24 * 60 * 60 * 1000;
  const daysToExpiry = Math.floor((exp.getTime() - now.getTime()) / msInDay);
  const isExpired = exp < now;
  const isExpiringSoon = !isExpired && daysToExpiry <= 14;

  // Defensive: fallback for invalid/missing dates
  let issuedDate: string = '';
  let expiresDate: string = '';
  try {
    issuedDate = issuedAt ? new Date(issuedAt).toLocaleString() : 'N/A';
  } catch {
    issuedDate = 'Invalid date';
  }
  try {
    expiresDate = expiresAt ? new Date(expiresAt).toLocaleString() : 'N/A';
  } catch {
    expiresDate = 'Invalid date';
  }

  return (
    <section className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 w-full max-w-xl mb-6 font-roboto relative" aria-label="License Information" tabIndex={0}>
      {/* Trial/Full Tag in upper right */}
      <span className="absolute top-4 right-4">
        <Badge
          variant="outline"
          className={`inline-flex items-center px-3 py-1 rounded font-mono text-xs font-semibold font-roboto ${isTrial ? 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200' : 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300'}`}
          aria-label={isTrial ? 'Trial License' : 'Full License'}
        >
          {isTrial ? 'Trial' : 'Full'}
        </Badge>
      </span>
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2 font-roboto">
        <ShieldCheck className="w-6 h-6 text-blue-500" aria-hidden="true" /> License Info
        <span className="sr-only">License status and details</span>
      </h2>
      {(isExpired || isExpiringSoon) && (
        <div className={`flex items-center gap-2 mb-4 p-2 rounded font-roboto ${isExpired ? "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300" : "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300"}`}
             role="alert"
             aria-live="assertive"
             tabIndex={0}>
          {isExpired ? (
            <AlertTriangle className="w-5 h-5 mr-1" aria-hidden="true" />
          ) : (
            <Clock className="w-5 h-5 mr-1" aria-hidden="true" />
          )}
          <span className="font-semibold">
            {isExpired ? "This license has expired." : `This license will expire in ${daysToExpiry} day${daysToExpiry !== 1 ? "s" : ""}.`}
          </span>
        </div>
      )}
      <dl className="space-y-2 font-roboto">
        <div>
          <dt className="font-semibold font-roboto">License Key</dt>
          <dd className="font-mono font-roboto">{licenseKey}</dd>
        </div>
        <div>
          <dt className="font-semibold font-roboto">Tier</dt>
          <dd className="font-roboto">
            <Badge
              variant="outline"
              className="inline-flex items-center px-3 py-1 rounded font-mono text-xs font-semibold bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300 font-roboto"
              aria-label={`License tier: ${normalizeTier(tier)}`}
            >
              {normalizeTier(tier)}
            </Badge>
          </dd>
        </div>
        <div>
          <dt className="font-semibold font-roboto">Status</dt>
          <dd className="font-roboto">
            {status === "Active" ? (
              <Badge
                variant="outline"
                className="inline-flex items-center px-3 py-1 rounded font-mono text-xs font-semibold bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 font-roboto"
                aria-label="License active"
              >
                Active
              </Badge>
            ) : (
              <Badge
                variant="outline"
                className="inline-flex items-center px-3 py-1 rounded font-mono text-xs font-semibold bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300 font-roboto"
                aria-label="License inactive"
              >
                {status}
              </Badge>
            )}
            <span className="ml-2 align-middle font-roboto" tabIndex={0} aria-label="More info about license status">
              <BadgeInfo className="w-4 h-4 text-gray-400 inline" aria-hidden="true" />
            </span>
          </dd>
        </div>
        <div>
          <dt className="font-semibold font-roboto">Issued At</dt>
          <dd className="font-roboto" title={issuedAt}>{issuedDate}</dd>
        </div>
        <div>
          <dt className="font-semibold font-roboto">Expires At</dt>
          <dd className="font-roboto" title={expiresAt}>{expiresDate}</dd>
        </div>
      </dl>
    </section>
  );
};
