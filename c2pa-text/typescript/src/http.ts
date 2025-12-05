/**
 * HTTP utilities for C2PA Text API calls.
 *
 * This module provides helper functions that correctly handle Unicode variation
 * selectors when making HTTP requests. Standard HTTP clients (especially in
 * PowerShell, curl on Windows, etc.) often corrupt these characters during
 * JSON serialization.
 *
 * @example
 * ```typescript
 * import { signText, verifyText } from 'c2pa-text/http';
 *
 * // Sign text
 * const signResult = await signText({
 *   apiUrl: 'https://api.encypherai.com/api/v1/sign',
 *   apiKey: 'your_api_key',
 *   text: 'Hello, world!',
 *   customMetadata: { author: 'Your Name' }
 * });
 *
 * // Verify text
 * const verifyResult = await verifyText({
 *   apiUrl: 'https://api.encypherai.com/api/v1/verify',
 *   apiKey: 'your_api_key',
 *   text: signResult.signed_text
 * });
 * ```
 */

export interface C2PAHTTPError extends Error {
  statusCode: number;
  responseBody?: string;
}

export interface SignTextOptions {
  /** The sign endpoint URL */
  apiUrl: string;
  /** Your API key */
  apiKey: string;
  /** The text to sign */
  text: string;
  /** Optional metadata to include in the manifest */
  customMetadata?: Record<string, unknown>;
  /** If true, use "Bearer {key}" auth. If false, use "X-API-Key" header. Default: true */
  useBearer?: boolean;
}

export interface VerifyTextOptions {
  /** The verify endpoint URL */
  apiUrl: string;
  /** Your API key */
  apiKey: string;
  /** The signed text to verify */
  text: string;
  /** If true, use "Bearer {key}" auth. If false, use "X-API-Key" header. Default: true */
  useBearer?: boolean;
}

export interface SignResponse {
  success: boolean;
  signed_text: string;
  document_id: string;
  verification_url: string;
  error?: { code: string; message: string };
  correlation_id: string;
}

export interface VerifyResponse {
  success: boolean;
  data: {
    valid: boolean;
    tampered: boolean;
    reason_code: string;
    signer_id: string | null;
    signer_name: string | null;
    timestamp: string | null;
    details: {
      manifest: Record<string, unknown>;
      duration_ms: number;
      payload_bytes: number;
    };
  };
  error: { code: string; message: string } | null;
  correlation_id: string;
}

/**
 * Create a C2PA HTTP error.
 */
function createHTTPError(statusCode: number, message: string, responseBody?: string): C2PAHTTPError {
  const error = new Error(`HTTP ${statusCode}: ${message}`) as C2PAHTTPError;
  error.name = 'C2PAHTTPError';
  error.statusCode = statusCode;
  error.responseBody = responseBody;
  return error;
}

/**
 * Make an HTTP request with proper UTF-8 encoding for C2PA text.
 *
 * This function ensures that Unicode variation selectors are correctly
 * preserved during JSON serialization and transmission.
 */
async function makeRequest<T>(
  url: string,
  method: string,
  headers: Record<string, string>,
  body?: Record<string, unknown>
): Promise<T> {
  const requestHeaders: Record<string, string> = {
    ...headers,
    'Content-Type': 'application/json; charset=utf-8',
  };

  const options: RequestInit = {
    method,
    headers: requestHeaders,
  };

  if (body !== undefined) {
    // JSON.stringify preserves Unicode characters by default in JavaScript
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  const responseText = await response.text();

  if (!response.ok) {
    throw createHTTPError(response.status, response.statusText, responseText);
  }

  return JSON.parse(responseText) as T;
}

/**
 * Sign text using the Encypher C2PA API.
 *
 * This function properly handles Unicode encoding to ensure the signed
 * text with variation selectors is correctly returned.
 *
 * @example
 * ```typescript
 * const result = await signText({
 *   apiUrl: 'https://api.encypherai.com/api/v1/sign',
 *   apiKey: 'ency_your_api_key',
 *   text: 'Hello, world!',
 *   customMetadata: { author: 'Alice' }
 * });
 * console.log(result.signed_text);
 * ```
 */
export async function signText(options: SignTextOptions): Promise<SignResponse> {
  const { apiUrl, apiKey, text, customMetadata, useBearer = true } = options;

  const headers: Record<string, string> = {};
  if (useBearer) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  } else {
    headers['X-API-Key'] = apiKey;
  }

  const body: Record<string, unknown> = { text };
  if (customMetadata) {
    body['custom_metadata'] = customMetadata;
  }

  return makeRequest<SignResponse>(apiUrl, 'POST', headers, body);
}

/**
 * Verify signed text using the Encypher C2PA API.
 *
 * This function properly handles Unicode variation selectors in the
 * signed text to ensure accurate verification.
 *
 * @example
 * ```typescript
 * const result = await verifyText({
 *   apiUrl: 'https://api.encypherai.com/api/v1/verify',
 *   apiKey: 'ency_your_api_key',
 *   text: signedText
 * });
 * console.log(`Valid: ${result.data.valid}`);
 * ```
 */
export async function verifyText(options: VerifyTextOptions): Promise<VerifyResponse> {
  const { apiUrl, apiKey, text, useBearer = true } = options;

  const headers: Record<string, string> = {};
  if (useBearer) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  } else {
    headers['X-API-Key'] = apiKey;
  }

  const body = { text };

  return makeRequest<VerifyResponse>(apiUrl, 'POST', headers, body);
}

/**
 * Sign text and immediately verify it (useful for testing).
 *
 * @example
 * ```typescript
 * const result = await signAndVerify({
 *   baseUrl: 'https://api.encypherai.com/api/v1',
 *   apiKey: 'ency_your_api_key',
 *   text: 'Test document'
 * });
 * console.log(`Signed: ${result.signResponse.success}`);
 * console.log(`Verified: ${result.verifyResponse.data.valid}`);
 * ```
 */
export async function signAndVerify(options: {
  baseUrl: string;
  apiKey: string;
  text: string;
  customMetadata?: Record<string, unknown>;
  useBearer?: boolean;
}): Promise<{ signResponse: SignResponse; verifyResponse: VerifyResponse }> {
  const { baseUrl, apiKey, text, customMetadata, useBearer = true } = options;

  const signUrl = `${baseUrl.replace(/\/$/, '')}/sign`;
  const verifyUrl = `${baseUrl.replace(/\/$/, '')}/verify`;

  const signResponse = await signText({
    apiUrl: signUrl,
    apiKey,
    text,
    customMetadata,
    useBearer,
  });

  const verifyResponse = await verifyText({
    apiUrl: verifyUrl,
    apiKey,
    text: signResponse.signed_text,
    useBearer,
  });

  return { signResponse, verifyResponse };
}
