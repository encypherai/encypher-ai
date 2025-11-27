import { useCallback, useState } from "react";
import { fetchApi } from "@/lib/api";
import nacl from "tweetnacl";
import naclUtil from "tweetnacl-util";
import { toPem } from "@/lib/pem";

// Unify and clarify UserKeyResponse type for all backend variants
export type UserKeyResponse =
  | { public_key: string | null }
  | { success: boolean; data?: { public_key: string | null; private_key?: string }; error?: { code: string; message: string; details?: unknown } };

interface FetchApiError extends Error {
  status?: number;
  error?: {
    message?: string;
  };
}

export function useUserKey(token?: string) {
  const [publicKey, setPublicKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate Ed25519 keypair client-side
  const generateKeyPair = useCallback(() => {
    setError(null);
    try {
      const keyPair = nacl.sign.keyPair();
      const publicKeyBase64 = naclUtil.encodeBase64(keyPair.publicKey);
      const privateKeyBase64 = naclUtil.encodeBase64(keyPair.secretKey);
      // Format as PEM
      const publicKeyPem = toPem(publicKeyBase64, 'public');
      const privateKeyPem = toPem(privateKeyBase64, 'private');
      // Do not send privateKey anywhere!
      return { publicKey: publicKeyPem, privateKey: privateKeyPem };
    } catch (err) {
      setError((err as Error).message || "Failed to generate key pair");
      return null;
    }
  }, []);

  // Upload public key to backend
  const uploadPublicKey = useCallback(async (publicKey: string) => {
    setLoading(true);
    setError(null);
    try {
      // Remove PEM header/footer for backend storage
      const base64Pub = publicKey.replace(/-----.*-----|\n/g, "").trim();
      const payload = { public_key: publicKey };
      // Rich debug logging
      console.debug('[DEBUG] [uploadPublicKey] Original publicKey:', publicKey);
      console.debug('[DEBUG] [uploadPublicKey] Stripped base64Pub:', base64Pub);
      console.debug('[DEBUG] [uploadPublicKey] Payload sent:', payload);
      const res = await fetchApi<UserKeyResponse>("/api/v1/keys/generate", {
        method: "POST",
        token,
        body: JSON.stringify(payload),
        headers: { "Content-Type": "application/json" },
      });
      if (res && (typeof res === 'object')) {
        let key: string | null = null;
        if ('public_key' in res) {
          key = res.public_key ?? null;
        } else if ('data' in res && typeof res.data === 'object' && 'public_key' in res.data) {
          key = res.data.public_key ?? null;
        }
        if (key) {
          setPublicKey(key);
          return true;
        } else {
          setError("Failed to upload public key");
          return false;
        }
      } else {
        setError("Failed to upload public key");
        return false;
      }
    } catch (err) {
      setError((err as Error).message || "Failed to upload public key");
      // Rich exception logging
      console.error('[ERROR] [uploadPublicKey] Exception:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const fetchPublicKey = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchApi<UserKeyResponse>("/api/v1/keys/public", { method: "GET", token });
      if (res && (typeof res === 'object')) {
        // Accept all backend shapes: {public_key}, {success, data: {public_key}}
        let key: string | null = null;
        if ('public_key' in res) {
          key = res.public_key ?? null;
        } else if ('data' in res && typeof res.data === 'object' && 'public_key' in res.data) {
          key = res.data.public_key ?? null;
        }
        setPublicKey(key);
        setError(null);
      } else {
        setPublicKey(null);
        // Check if res has an error property with a message
        const errorMessage = (res as FetchApiError)?.error?.message;
        setError(errorMessage ?? null);
        console.error('[ERROR] [fetchPublicKey] API Error:', errorMessage ?? 'Unknown error structure');
      }
    } catch (err) {
      const error = err as FetchApiError; // Type assertion
      console.error('[ERROR] [fetchPublicKey] Caught Error:', error);
      // Check if it's a 404 error
      if (error?.status === 404) {
        console.log('[INFO] [fetchPublicKey] Received 404, treating as no public key found.');
        setPublicKey(null); // No key found is expected
        setError(null);     // This is not an error state
      } else {
        // Handle other errors as actual errors
        setPublicKey(null);
        setError(error.message || "Failed to fetch public key");
      }
    } finally {
      setLoading(false);
    }
  }, [token]);

  return { publicKey, loading, error, fetchPublicKey, generateKeyPair, uploadPublicKey };
}
