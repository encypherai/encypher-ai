"use client";
import React, { useState } from "react";
import { KeyRound, Pencil, Eye, EyeOff, BadgeCheck, Copy, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { fetchApi } from "@/lib/api";
import { useSession } from "next-auth/react";
import { saveAs } from "file-saver";

export type OrgPublicKeyCardProps = {
  publicKey: string;
  onPublicKeyUpdated?: (newKey: string) => void;
};

export const OrgPublicKeyCard: React.FC<OrgPublicKeyCardProps> = ({
  publicKey,
  onPublicKeyUpdated,
}) => {
  const [editing, setEditing] = useState(false);
  const [input, setInput] = useState(publicKey);
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);

  // Update session typing to include user role for type safety
  const { data: session } = useSession() as { data: { accessToken?: string; user?: { role?: string } } | null };

  // Helper: check if user is admin (OrgAdmin or OrgOwner)
  const isAdmin = session?.user?.role && (
    session.user.role.endsWith('Admin') || session.user.role.endsWith('Owner')
  );

  // Helper: only add PEM headers/footers if missing
  function normalizePem(pem: string): string {
    const lines = pem.trim().split(/\r?\n/);
    const contentLines = lines.filter(
      (line, idx, arr) =>
        !(line.startsWith('-----BEGIN') && idx !== 0) &&
        !(line.startsWith('-----END') && idx !== arr.length - 1)
    );
    const cleaned = contentLines.join('\n').replace(/\n{2,}/g, '\n');
    return cleaned;
  }

  const handleSave = async () => {
    setLoading(true);
    try {
      if (!session?.accessToken) throw new Error("Not authenticated");
      await fetchApi("/api/v1/org-keys", {
        method: editing && publicKey ? "PUT" : "POST",
        token: session.accessToken,
        body: JSON.stringify({ public_key: input }),
      });
      toast.success("Organization public key updated");
      setEditing(false);
      if (onPublicKeyUpdated) onPublicKeyUpdated(input);
    } catch (err: unknown) {
      const error = err as Error;
      toast.error(error.message || "Failed to update organization public key");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="relative bg-white/80 dark:bg-gray-900/70 rounded-2xl shadow-lg ring-1 ring-gray-200 dark:ring-gray-800 p-8 w-full max-w-xl mb-8 backdrop-blur-md font-roboto" aria-label="Organization Public Key" tabIndex={0}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold flex items-center gap-2 font-roboto">
          <span className="sr-only">Organization Public Key Section</span>
          <KeyRound className="w-6 h-6 text-indigo-500" /> Organization Public Key
        </h2>
        {isAdmin && !editing && (
          <Button
            onClick={() => setEditing(true)}
            size="icon"
            className="rounded-full bg-gradient-to-r from-blue-600 to-indigo-500 hover:from-blue-700 hover:to-indigo-600 font-roboto"
            aria-label="Edit public key"
            variant="ghost"
            disabled={loading}
          >
            <Pencil className="w-5 h-5 text-white" />
          </Button>
        )}
      </div>
      {!editing ? (
        <div className="flex flex-col gap-4 font-roboto">
          {publicKey ? (
            <>
              <div className="flex items-center gap-2 font-roboto">
                <Button variant="ghost" size="icon" aria-label="Toggle key visibility" onClick={() => setShow((v) => !v)} className="font-roboto">
                  {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
                <BadgeCheck className="w-4 h-4 text-green-500" />
                <span className="text-xs text-gray-500 dark:text-gray-300">This key is used to verify content signed by your organization.</span>
              </div>
              {show && (
                <>
                  <Textarea value={normalizePem(publicKey)} readOnly rows={4} className="font-mono text-xs mt-2" aria-label="Organization public key" />
                  <div className="flex gap-2 mt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        navigator.clipboard.writeText(normalizePem(publicKey));
                        toast.success("Public key copied");
                      }}
                      aria-label="Copy organization public key"
                    >
                      <Copy className="w-4 h-4 mr-1" /> Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const blob = new Blob([normalizePem(publicKey)], { type: "application/x-pem-file" });
                        saveAs(blob, "encypherai-org-public-key.pem");
                      }}
                      aria-label="Download organization public key as PEM"
                    >
                      <PlusCircle className="w-4 h-4 mr-1" /> Download
                    </Button>
                  </div>
                </>
              )}
            </>
          ) : (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-300 font-roboto">
              No public key set for organization
            </span>
          )}
        </div>
      ) : (
        <div className="flex flex-col gap-4 font-roboto">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={6}
            placeholder="Paste PEM public key here"
            className="font-mono text-xs font-roboto"
            aria-label="Organization public key"
          />
          <div className="flex gap-2 font-roboto">
            <Button onClick={handleSave} disabled={loading || !input.trim()} className="font-roboto">
              Save
            </Button>
            <Button variant="secondary" onClick={() => { setEditing(false); setInput(publicKey); }} className="font-roboto">
              Cancel
            </Button>
          </div>
        </div>
      )}
    </section>
  );
};
