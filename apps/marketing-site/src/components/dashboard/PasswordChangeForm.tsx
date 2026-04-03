"use client";
import React, { useState } from "react";
import { Button } from "@encypher/design-system";
import { Input } from "@encypher/design-system";
import { useSession } from "next-auth/react";
import { fetchApi } from "@/lib/api";
import { useToast } from "@encypher/design-system";

// Add onSuccess prop for modal integration
export const PasswordChangeForm: React.FC<{ onSuccess?: () => void }> = ({ onSuccess }) => {
  const { data: session } = useSession();
  const { toast } = useToast();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    if (!session?.accessToken) {
      setError("Not authenticated.");
      return;
    }
    if (!next || next.length < 8) {
      setError("New password must be at least 8 characters.");
      return;
    }
    if (next !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetchApi("/api/v1/users/me/password", {
        method: "PUT",
        token: session.accessToken,
        body: JSON.stringify({ current_password: current, new_password: next }),
      }) as { success?: boolean; error?: { message?: string } };
      if (res.success) {
        setSuccess(true);
        setCurrent("");
        setNext("");
        setConfirm("");
        toast({ title: "Password updated" });
        if (onSuccess) onSuccess();
      } else {
        setError(res.error?.message || "Failed to update password.");
      }
    } catch {
      setError("Failed to update password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto" aria-label="Change Password Form">
      {/* <h3 className="text-lg font-semibold">Change Password</h3> */}
      <Input
        type="password"
        value={current}
        onChange={e => setCurrent(e.target.value)}
        placeholder="Current password"
        required
        aria-label="Current password"
      />
      <Input
        type="password"
        value={next}
        onChange={e => setNext(e.target.value)}
        placeholder="New password"
        minLength={8}
        required
        aria-label="New password"
      />
      <Input
        type="password"
        value={confirm}
        onChange={e => setConfirm(e.target.value)}
        placeholder="Confirm new password"
        minLength={8}
        required
        aria-label="Confirm new password"
      />
      {error && <div className="text-red-600 text-sm">{error}</div>}
      {success && <div className="text-green-600 text-sm">Password updated successfully.</div>}
      <Button type="submit" disabled={loading} aria-busy={loading}>Change Password</Button>
    </form>
  );
};
