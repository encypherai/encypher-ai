"use client";
import React, { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { User2, ShieldCheck, Crown, Lock } from "lucide-react";
import { useSession } from "next-auth/react";
import { fetchApi } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import { PasswordChangeForm } from "./PasswordChangeForm";

export type UserProfileCardProps = {
  email: string;
  role: string;
  isActive: boolean;
};

export const UserProfileCard: React.FC<UserProfileCardProps> = ({
  email,
  role,
  isActive,
}) => {
  const { data: session } = useSession();
  const { toast } = useToast();
  const [emailUpdates, setEmailUpdates] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPasswordModal, setShowPasswordModal] = useState(false);

  // Fetch email_updates on mount
  useEffect(() => {
    const fetchSettings = async () => {
      if (!session?.accessToken) return;
      try {
        setLoading(true);
        setError(null);
        const res = await fetchApi("/api/v1/users/me", {
          method: "GET",
          token: session.accessToken,
        }) as { email_updates?: boolean };
        if (res && typeof res.email_updates === "boolean") {
          setEmailUpdates(res.email_updates);
        }
      } catch (err) {
        setError("Failed to load notification settings");
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, [session?.accessToken]);

  // Toggle handler
  const handleToggle = async () => {
    if (!session?.accessToken) return;
    try {
      setLoading(true);
      setError(null);
      const res = await fetchApi("/api/v1/users/me", {
        method: "PUT",
        token: session.accessToken,
        body: JSON.stringify({ email_updates: !emailUpdates }),
      }) as { email_updates?: boolean };
      if (res && typeof res.email_updates === "boolean") {
        setEmailUpdates(res.email_updates);
        toast({ title: "Email updates preference saved" });
      } else {
        setError("Failed to save notification settings");
      }
    } catch (err) {
      setError("Failed to save notification settings");
    } finally {
      setLoading(false);
    }
  };

  // Normalize role for consistent display and logic
  let normalizedRole = role;
  if (typeof normalizedRole === 'string' && normalizedRole.includes('.')) {
    normalizedRole = normalizedRole.split('.').pop() || normalizedRole;
  }
  if (typeof normalizedRole === 'string' && normalizedRole.startsWith('Org')) {
    normalizedRole = normalizedRole.replace(/^Org/, '');
  }

  return (
    <section
      className="relative bg-white/80 dark:bg-gray-900/70 rounded-2xl shadow-lg ring-1 ring-gray-200 dark:ring-gray-800 p-8 w-full max-w-xl mb-8 backdrop-blur-md font-roboto"
      aria-label="User Profile"
      tabIndex={0}
    >
      <div className="flex items-center gap-4 mb-6">
        <div className="flex-shrink-0 w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-md">
          <User2 className="text-white w-8 h-8" aria-label="User avatar" />
        </div>
        <div className="flex flex-col gap-1">
          <span className="text-lg font-semibold text-gray-900 dark:text-gray-100 font-roboto" tabIndex={0}>{email}</span>
          <span className="text-sm text-gray-500 dark:text-gray-300 font-roboto" tabIndex={0}>
            {normalizedRole}
          </span>
        </div>
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 font-roboto">
        <dt className="text-gray-500 dark:text-gray-400 font-semibold flex items-center gap-2 font-roboto" id="user-role-label">Role</dt>
        <dd className="font-roboto" tabIndex={0} aria-labelledby="user-role-label">
          <Badge
            variant="outline"
            className={`inline-flex items-center gap-1 px-3 py-1 w-fit whitespace-nowrap font-mono text-xs font-semibold
              ${normalizedRole === 'Admin' ? 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/40 dark:text-yellow-300 dark:border-yellow-700'
                : normalizedRole === 'Owner' ? 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/40 dark:text-orange-300 dark:border-orange-700'
                : 'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/40 dark:text-blue-300 dark:border-blue-700'}
            `}
            aria-label={normalizedRole}
          >
            {normalizedRole === 'Admin' && <ShieldCheck className="w-4 h-4 mr-1" aria-label="Admin icon" />}
            {normalizedRole === 'Owner' && <Crown className="w-4 h-4 mr-1" aria-label="Owner icon" />}
            {normalizedRole === 'User' && <User2 className="w-4 h-4 mr-1" aria-label="User icon" />}
            {normalizedRole}
          </Badge>
        </dd>
        <dt className="text-gray-500 dark:text-gray-400 font-semibold flex items-center gap-2 font-roboto">Status</dt>
        <dd>
          <Badge
            variant="outline"
            className={`px-3 py-1 ${isActive ? 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/40 dark:text-green-300 dark:border-green-700' : 'bg-gray-200 text-gray-600 border-gray-300 dark:bg-gray-800/40 dark:text-gray-400 dark:border-gray-700'} font-roboto`}
            aria-label={`User status: ${isActive ? 'Active' : 'Inactive'}`}
            tabIndex={0}
          >
            {isActive ? "Active" : "Inactive"}
          </Badge>
        </dd>
        {/* Email Updates Toggle */}
        <dt className="text-gray-500 dark:text-gray-400 font-semibold flex items-center gap-2 font-roboto" id="email-updates-label">
          Email Updates
        </dt>
        <dd>
          <div className="flex items-center gap-3 min-h-[44px]">
            <Switch
              checked={emailUpdates}
              onCheckedChange={handleToggle}
              disabled={loading}
              aria-labelledby="email-updates-label"
              aria-checked={emailUpdates}
              aria-busy={loading}
              className="focus-visible:ring-2 focus-visible:ring-blue-500"
            />
            <span
              className={`flex items-center gap-1 text-sm font-medium font-roboto select-none ${emailUpdates ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'}`}
              aria-live="polite"
              id="email-updates-state-label"
            >
              {/* Mail icon color reflects state */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className={`w-4 h-4 ${emailUpdates ? 'text-green-500 dark:text-green-300' : 'text-gray-400 dark:text-gray-500'}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
                focusable="false"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a3 3 0 003.22 0L22 8m-19 8V8a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              </svg>
              {emailUpdates ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          {error && <div className="text-red-600 text-xs mt-1">{error}</div>}
        </dd>
      </dl>
      <div className="flex justify-end mt-6">
        <Button variant="outline" onClick={() => setShowPasswordModal(true)}>
          <Lock className="w-4 h-4 mr-2" /> Change Password
        </Button>
      </div>
      {/* Password Change Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6 w-full max-w-md relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
              onClick={() => setShowPasswordModal(false)}
              aria-label="Close password change dialog"
            >
              ×
            </button>
            <h3 className="text-lg font-semibold mb-4">Change Password</h3>
            <PasswordChangeForm onSuccess={() => setShowPasswordModal(false)} />
          </div>
        </div>
      )}
    </section>
  );
};
