"use client";
import React, { useState, useRef, useEffect } from "react";
import { KeyRound, Eye, EyeOff, BadgeCheck, Copy, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useUserKey } from "@/lib/hooks/useUserKey";
import { useSession } from "next-auth/react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { saveAs } from "file-saver";
import { useOrganization } from "@/lib/hooks/useOrganization";

export const UserKeyCard: React.FC = () => {
  const { data: session } = useSession() as { data: { accessToken?: string } | null };
  const token = session?.accessToken;
  const { publicKey, loading, error, fetchPublicKey, generateKeyPair, uploadPublicKey } = useUserKey(token);
  const { org, isLoading: orgLoading, error: orgError } = useOrganization();
  const [show, setShow] = useState(false);
  const [privateKey, setPrivateKey] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [checkboxChecked, setCheckboxChecked] = useState(false);
  const [pendingPub, setPendingPub] = useState<string | null>(null);

  const firstInputRef = useRef<HTMLInputElement | null>(null);
  const continueBtnRef = useRef<HTMLButtonElement | null>(null);

  // Focus trap: when modal opens, focus first input
  useEffect(() => {
    if (modalOpen && firstInputRef.current) {
      firstInputRef.current.focus();
    }
  }, [modalOpen]);

  React.useEffect(() => { if (token) fetchPublicKey(); }, [token, fetchPublicKey]);

  // Restriction logic: Only allow keypair generation if permitted by org tier and org key status
  const orgTier = org?.revenue_tier?.toLowerCase();
  const orgHasOrgKey = Boolean(org?.latest_org_public_key);
  const isStartupOrFree = orgTier === "startup" || orgTier === "free";
  const restrictKeyGen = isStartupOrFree && orgHasOrgKey && !publicKey;

  const handleGenerate = () => {
    const keypair = generateKeyPair();
    if (keypair) {
      setPrivateKey(keypair.privateKey);
      setPendingPub(keypair.publicKey);
      setModalOpen(true);
      setCheckboxChecked(false);
      toast.success("Key pair generated. Save your private key!");
    }
  };

  const handleCopy = () => {
    if (privateKey) {
      navigator.clipboard.writeText(privateKey);
      toast.success("Private key copied");
    }
  };

  const handleCopyPub = () => {
    if (pendingPub) {
      navigator.clipboard.writeText(pendingPub);
      toast.success("Public key copied");
    }
  };

  const handleDownload = () => {
    if (privateKey) {
      const blob = new Blob([privateKey], { type: "application/x-pem-file" });
      saveAs(blob, "encypherai-private-key.pem");
    }
  };

  const handleDownloadPub = () => {
    if (pendingPub) {
      const blob = new Blob([pendingPub], { type: "application/x-pem-file" });
      saveAs(blob, "encypherai-public-key.pem");
    }
  };

  const handleConfirm = async () => {
    if (!pendingPub) return;
    if (!checkboxChecked) return;
    const success = await uploadPublicKey(pendingPub);
    if (success) {
      setModalOpen(false);
      setPrivateKey(null);
      setPendingPub(null);
      setCheckboxChecked(false);
      toast.success("Public key uploaded successfully!");
      window.location.reload();
    }
  };

  // Helper: only add PEM headers/footers if missing
  function normalizePem(pem: string): string {
    // Remove duplicate headers/footers
    const lines = pem.trim().split(/\r?\n/);
    const contentLines = lines.filter(
      (line, idx, arr) =>
        !(line.startsWith('-----BEGIN') && idx !== 0) &&
        !(line.startsWith('-----END') && idx !== arr.length - 1)
    );
    // Remove extra blank lines
    const cleaned = contentLines.join('\n').replace(/\n{2,}/g, '\n');
    return cleaned;
  }

  return (
    <section className="relative bg-white/80 dark:bg-gray-900/70 rounded-2xl shadow-lg ring-1 ring-gray-200 dark:ring-gray-800 p-8 w-full max-w-xl mb-8 backdrop-blur-md font-roboto" aria-label="User Public Key" tabIndex={0}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold flex items-center gap-2 font-roboto">
          <span className="sr-only">User Public Key Section</span>
          <KeyRound className="w-6 h-6 text-indigo-500" /> My Signing Key
        </h2>
      </div>
      <div className="flex flex-col gap-2 font-roboto">
        {publicKey ? (
          <>
            <div className="flex items-center gap-2 font-roboto">
              <Button variant="ghost" size="icon" aria-label="Toggle key visibility" onClick={() => setShow((v) => !v)} className="font-roboto">
                {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>
              <BadgeCheck className="w-4 h-4 text-green-500" />
              <span className="text-xs text-gray-500 dark:text-gray-300">Your public key is used to verify content you sign.</span>
            </div>
            {show && (
              <>
                <Textarea value={publicKey ? normalizePem(publicKey) : ""} readOnly rows={4} className="font-mono text-xs mt-2" aria-label="User public key" />
                <div className="flex gap-2 mt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      if (publicKey) {
                        navigator.clipboard.writeText(normalizePem(publicKey));
                        toast.success("Public key copied");
                      }
                    }}
                    aria-label="Copy public key"
                  >
                    <Copy className="w-4 h-4 mr-1" /> Copy
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      if (publicKey) {
                        const blob = new Blob([normalizePem(publicKey)], { type: "application/x-pem-file" });
                        saveAs(blob, "encypherai-public-key.pem");
                      }
                    }}
                    aria-label="Download public key as PEM"
                  >
                    <PlusCircle className="w-4 h-4 mr-1" /> Download
                  </Button>
                </div>
              </>
            )}
          </>
        ) : restrictKeyGen ? (
          <div className="flex flex-col gap-2">
            <Button disabled className="flex items-center gap-2 font-roboto opacity-60 cursor-not-allowed" aria-label="Key pair generation disabled">
              <PlusCircle className="w-4 h-4" /> Generate My Key Pair
            </Button>
            <div className="text-sm text-yellow-700 dark:text-yellow-300 bg-yellow-50 dark:bg-yellow-900/30 rounded p-2 mt-1" role="alert" aria-live="polite">
              <b>Key generation restricted:</b> Your organization is on the <b>Startup</b> or <b>Free</b> tier and already has an organization key. Only one key pair is allowed per organization on this tier. Upgrade to <b>Growth</b> or <b>Enterprise</b> to allow multiple user keys.
            </div>
          </div>
        ) : (
          <Button onClick={handleGenerate} disabled={loading || orgLoading} className="flex items-center gap-2 font-roboto" aria-label="Generate key pair">
            <PlusCircle className="w-4 h-4" /> Generate My Key Pair
          </Button>
        )}
        {error && <div className="text-red-500 text-xs mt-2" role="alert">{error}</div>}
        {orgError && <div className="text-red-500 text-xs mt-2" role="alert">{orgError.message}</div>}
      </div>
      <Dialog
        open={modalOpen}
        onOpenChange={open => {
          // Prevent closing by outside click or Escape
          if (open === false) return;
          setModalOpen(open);
        }}
        modal
      >
        <DialogContent
          className="w-full max-w-sm p-4 rounded-xl shadow-xl bg-white dark:bg-gray-900 overflow-visible flex flex-col gap-4"
          onInteractOutside={e => e.preventDefault()} // disables outside click close
          onEscapeKeyDown={e => e.preventDefault()} // disables Escape key close
        >
          <DialogHeader>
            <DialogTitle id="save-key-title" className="text-lg md:text-xl">Save Your Keys</DialogTitle>
          </DialogHeader>
          {/* Private Key Section */}
          <div className="flex flex-col gap-1">
            <label htmlFor="private-key" className="font-semibold text-sm">Your Private Key</label>
            <Textarea id="private-key" value={privateKey || ""} readOnly rows={4} className="font-mono text-xs resize-none min-h-[72px]" aria-label="User private key" tabIndex={0} />
            <div className="flex gap-2 flex-wrap mt-1">
              <Button onClick={handleCopy} className="flex-1 min-w-[44px] min-h-[44px] text-xs px-2 py-1" aria-label="Copy private key">
                <Copy className="w-4 h-4" /> Copy Private Key
              </Button>
              <Button onClick={handleDownload} className="flex-1 min-w-[44px] min-h-[44px] text-xs px-2 py-1" aria-label="Download private key">
                <PlusCircle className="w-4 h-4" /> Download (.pem)
              </Button>
            </div>
          </div>
          {/* Public Key Section */}
          <div className="flex flex-col gap-1">
            <label htmlFor="public-key" className="font-semibold text-sm">Your Public Key</label>
            <Textarea id="public-key" value={pendingPub || ""} readOnly rows={3} className="font-mono text-xs resize-none min-h-[56px]" aria-label="User public key" tabIndex={0} />
            <div className="flex gap-2 flex-wrap mt-1">
              <Button onClick={handleCopyPub} className="flex-1 min-w-[44px] min-h-[44px] text-xs px-2 py-1" aria-label="Copy public key">
                <Copy className="w-4 h-4" /> Copy Public Key
              </Button>
              <Button onClick={handleDownloadPub} className="flex-1 min-w-[44px] min-h-[44px] text-xs px-2 py-1" aria-label="Download public key">
                <PlusCircle className="w-4 h-4" /> Download (.pem)
              </Button>
            </div>
          </div>
          <div className="text-xs text-yellow-800 dark:text-yellow-200 bg-yellow-50 dark:bg-yellow-900/30 rounded p-2 mt-1">
            <b>Important:</b> This is your <b>private key</b>. It will not be shown again. Copy and store it securely. If you lose it, it cannot be recovered!
          </div>
          <label className="flex items-center gap-2 mt-2 text-xs">
            <input
              ref={firstInputRef}
              type="checkbox"
              checked={checkboxChecked}
              onChange={e => setCheckboxChecked(e.target.checked)}
              aria-checked={checkboxChecked}
              aria-label="I have securely saved my private key and understand it cannot be shown again."
            />
            <span>I have securely saved my private key and understand it cannot be shown again.</span>
          </label>
          <div className="text-xs text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-800/30 rounded p-2 mt-1">
            <b>Troubleshooting:</b>
            <ul className="list-disc pl-4">
              <li>If the download or copy doesn’t work, try a different browser or disable extensions that block downloads/clipboard.</li>
              <li>Check your browser’s permissions for clipboard and downloads.</li>
              <li>Contact <a href="mailto:support@encypherai.com" className="underline">support@encypherai.com</a> for help.</li>
            </ul>
          </div>
          <DialogFooter className="flex justify-center mt-4">
            <Button
              ref={continueBtnRef}
              variant="default"
              className="w-48 mx-auto"
              onClick={handleConfirm}
              disabled={!checkboxChecked}
              aria-label="Continue and save public key"
            >
              Continue
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
};
