"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { fetchApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Lock, CheckCircle2, RefreshCw } from "lucide-react";

interface LicenseOut {
  uuid: string;
  status: string; // e.g., Active, Revoked, Expired
  is_trial?: boolean;
  tier?: { value?: string } | string;
  expires_at?: string;
}

function isActive(lic?: LicenseOut | null) {
  if (!lic) return false;
  const status = (lic.status || "").toLowerCase();
  if (status !== "active") return false;
  if (lic.expires_at) {
    const exp = new Date(lic.expires_at).getTime();
    if (!isNaN(exp) && Date.now() > exp) return false;
  }
  return true;
}

export default function EnterpriseToolsPanel() {
  const { data: session } = useSession();
  const [license, setLicense] = useState<LicenseOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Upgrade form state
  const [email, setEmail] = useState<string>("");
  const [message, setMessage] = useState<string>("I would like to upgrade to an enterprise license.");

  useEffect(() => {
    const run = async () => {
      if (!session?.accessToken) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        setError(null);
        const lic = await fetchApi<LicenseOut>("/api/v1/license/me", {
          method: "GET",
          token: session.accessToken,
        });
        setLicense(lic);
      } catch (e: any) {
        setError(e?.message || "Failed to load license status");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [session?.accessToken]);

  const active = isActive(license);

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-muted-foreground">
        <RefreshCw className="h-4 w-4 animate-spin" />
        Loading enterprise tools...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Enterprise Tools</h2>
          {license ? (
            <p className="text-sm text-muted-foreground">
              License: {(typeof license.tier === "string" ? license.tier : license.tier?.value) || "N/A"}
              {license.is_trial ? " (Trial)" : ""} • Status: {license.status}
              {license.expires_at ? ` • Expires: ${new Date(license.expires_at).toLocaleDateString()}` : ""}
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">No license info available.</p>
          )}
        </div>
        {active ? (
          <div className="flex items-center gap-2 text-green-700">
            <CheckCircle2 className="h-5 w-5" /> Active
          </div>
        ) : (
          <div className="flex items-center gap-2 text-amber-700">
            <Lock className="h-5 w-5" /> Locked
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Encode File Card */}
        <div className={`border rounded-lg p-5 bg-card shadow-sm ${active ? "" : "opacity-60"}`}>
          <h3 className="text-lg font-semibold mb-2">Encode File</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Embed Encypher metadata and verified signatures in supported files.
          </p>
          {active ? (
            <Link href="/tools/encode-file" className="inline-block">
              <Button>Open Encode</Button>
            </Link>
          ) : (
            <Button variant="secondary" disabled className="inline-flex items-center gap-2">
              <Lock className="h-4 w-4" /> Requires Enterprise License
            </Button>
          )}
        </div>

        {/* Decode/Scan File Card */}
        <div className={`border rounded-lg p-5 bg-card shadow-sm ${active ? "" : "opacity-60"}`}>
          <h3 className="text-lg font-semibold mb-2">Decode/Scan File</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Extract Encypher metadata and verify signatures from uploaded files.
          </p>
          {active ? (
            <Link href="/tools/decode-file" className="inline-block">
              <Button>Open Decode</Button>
            </Link>
          ) : (
            <Button variant="secondary" disabled className="inline-flex items-center gap-2">
              <Lock className="h-4 w-4" /> Requires Enterprise License
            </Button>
          )}
        </div>
      </div>

      {!active && (
        <div className="border rounded-lg p-5 bg-amber-50 border-amber-200">
          <h4 className="font-semibold mb-2">Request Enterprise Upgrade</h4>
          <p className="text-sm text-amber-800 mb-4">
            Your organization does not have an active license. Request an upgrade and our team will contact you.
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const to = "sales@encypherai.com";
              const subject = encodeURIComponent("Enterprise License Upgrade Request");
              const body = encodeURIComponent(`Email: ${email}\n\n${message}`);
              window.location.href = `mailto:${to}?subject=${subject}&body=${body}`;
            }}
            className="space-y-3"
          >
            <Input
              type="email"
              placeholder="Your work email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Textarea
              placeholder="Tell us about your use case"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={4}
            />
            <div className="flex gap-3">
              <Button type="submit">Request Upgrade</Button>
              <a
                href="mailto:sales@encypherai.com?subject=Enterprise%20License%20Upgrade%20Request"
                className="inline-flex items-center"
              >
                <Button type="button" variant="outline">Email Sales</Button>
              </a>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
