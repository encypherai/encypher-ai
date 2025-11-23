"use client";
import React, { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { fetchApi } from "@/lib/api";
import type { Invitation } from "@/types/invitation";
import { useOrganization } from "@/lib/hooks/useOrganization";
import { useToast } from "@/components/ui/use-toast";

// Add error response type for API error handling
type ApiErrorResponse = { error: { message: string } };
type ApiSuccessResponse = { success: boolean };

/**
 * InvitationsPanel component displays a list of pending invitations and allows users to invite new users.
 */
export const InvitationsPanel: React.FC = () => {
  const { data: session } = useSession();
  const { org } = useOrganization();
  const { toast } = useToast();
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteError, setInviteError] = useState<string | null>(null);

  /**
   * Type guard for API error response.
   * Checks if the response is an object with an error property containing a message.
   */
  function isApiErrorResponse(res: unknown): res is ApiErrorResponse {
    return (
      typeof res === "object" &&
      res !== null &&
      "error" in (res as Record<string, unknown>) &&
      typeof (res as { error?: unknown }).error === "object" &&
      (res as { error?: unknown }).error !== null &&
      "message" in (res as { error: { message?: unknown } }).error &&
      typeof ((res as { error: { message?: unknown } }).error as { message?: unknown }).message === "string"
    );
  }

  /**
   * Type guard for API success response.
   * Checks if the response is an object with a success property containing a boolean value.
   */
  function isApiSuccessResponse(res: unknown): res is ApiSuccessResponse {
    return (
      typeof res === "object" &&
      res !== null &&
      "success" in (res as Record<string, unknown>) &&
      typeof (res as { success?: unknown }).success === "boolean"
    );
  }

  useEffect(() => {
    const fetchInvites = async () => {
      if (!org?.uuid || !session?.accessToken) return;
      setLoading(true);
      setError(null);
      try {
        const res: unknown = await fetchApi(`/api/v1/invitations/organizations/${org.uuid}/invitations`, {
          method: "GET",
          token: session.accessToken,
        });
        if (Array.isArray(res)) {
          setInvitations(res as Invitation[]);
        } else if (isApiErrorResponse(res)) {
          setError(res.error.message);
        } else {
          setError("Failed to fetch invitations.");
        }
      } catch (err) {
        setError((err as Error)?.message || "Failed to fetch invitations.");
      } finally {
        setLoading(false);
      }
    };
    fetchInvites();
  }, [org, session]);

  const handleRevoke = async (token: string) => {
    if (!session?.accessToken) return;
    try {
      const res: unknown = await fetchApi(`/api/v1/invitations/invitations/${token}`, {
        method: "DELETE",
        token: session.accessToken,
      });
      if (isApiSuccessResponse(res) && res.success) {
        setInvitations((prev) => prev.map(inv => inv.token === token ? { ...inv, status: "revoked" } : inv));
        toast({ title: "Invitation Revoked" });
      } else if (isApiErrorResponse(res)) {
        toast({ title: "Error", description: res.error.message || "Failed to revoke invitation.", variant: "error" });
      } else {
        toast({ title: "Error", description: "Failed to revoke invitation.", variant: "error" });
      }
    } catch (err) {
      toast({ title: "Error", description: (err as Error)?.message || "Failed to revoke invitation.", variant: "error" });
    }
  };

  const handleInviteUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!org?.uuid || !session?.accessToken) return;
    setInviteLoading(true);
    setInviteError(null);
    try {
      const res: unknown = await fetchApi(`/api/v1/invitations/organizations/${org.uuid}/invitations`, {
        method: "POST",
        token: session.accessToken,
        body: JSON.stringify({ invitee_email: inviteEmail }),
      });
      if (isApiSuccessResponse(res) && res.success) {
        toast({ title: "Invitation Sent", description: `Invitation sent to ${inviteEmail}` });
        setInviteModalOpen(false);
        setInviteEmail("");
        // Refresh invitations
        setLoading(true);
        const refreshed = await fetchApi(`/api/v1/invitations/organizations/${org.uuid}/invitations`, {
          method: "GET",
          token: session.accessToken,
        });
        if (Array.isArray(refreshed)) {
          setInvitations(refreshed as Invitation[]);
        }
      } else if (isApiErrorResponse(res)) {
        setInviteError(res.error.message);
      } else {
        setInviteError("Failed to send invitation.");
      }
    } catch (err) {
      setInviteError((err as Error)?.message || "Failed to send invitation.");
    } finally {
      setInviteLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Pending Invitations</h2>
        <Button onClick={() => setInviteModalOpen(true)}>Invite User</Button>
      </div>
      <Dialog open={inviteModalOpen} onOpenChange={setInviteModalOpen}>
        <DialogContent>
          <form onSubmit={handleInviteUser} className="flex flex-col gap-4">
            <label htmlFor="invite-email" className="text-sm font-medium">Invitee Email</label>
            <input
              id="invite-email"
              type="email"
              value={inviteEmail}
              onChange={e => setInviteEmail(e.target.value)}
              required
              className="rounded border px-3 py-2 dark:bg-gray-800 dark:text-white"
              placeholder="user@example.com"
              aria-label="Invitee Email"
            />
            {inviteError && <div className="text-red-600 dark:text-red-400">{inviteError}</div>}
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="secondary" onClick={() => setInviteModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={inviteLoading || !inviteEmail}>
                {inviteLoading ? "Inviting..." : "Send Invite"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
      {loading ? (
        <div>Loading...</div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : invitations.length === 0 ? (
        <div>No pending invitations.</div>
      ) : (
        <table className="min-w-full text-sm border rounded">
          <thead>
            <tr>
              <th>Email</th>
              <th>Status</th>
              <th>Expires At</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {invitations.map(invite => (
              <tr key={invite.token} className={invite.status === "revoked" ? "opacity-50" : ""}>
                <td>{invite.invitee_email}</td>
                <td>{invite.status}</td>
                <td>{invite.expires_at ? new Date(invite.expires_at).toLocaleString() : "N/A"}</td>
                <td>
                  {invite.status === "pending" && (
                    <Button variant="destructive" size="sm" onClick={() => handleRevoke(invite.token)}>
                      Revoke
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
