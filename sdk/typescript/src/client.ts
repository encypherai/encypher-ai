/**
 * Encypher SDK - TypeScript client for the Encypher Enterprise API.
 *
 * This is an auto-generated SDK. For the source, see:
 * https://github.com/encypherai/encypherai-commercial/tree/main/sdk
 *
 * @example
 * ```typescript
 * import { EncypherClient } from '@encypher/sdk';
 *
 * const client = new EncypherClient({ apiKey: 'your_api_key' });
 * const result = await client.sign({ text: 'Hello, world!' });
 * console.log(result.signedText);
 * ```
 */

import { Configuration } from './runtime';
import { SigningApi, VerificationApi } from './apis';
import type { UnifiedSignRequest, VerifyRequest } from './models';

export interface EncypherClientOptions {
  apiKey: string;
  baseUrl?: string;
}

export class EncypherClient {
  private config: Configuration;
  private signing: SigningApi;
  private verification: VerificationApi;

  constructor(options: EncypherClientOptions) {
    this.config = new Configuration({
      basePath: options.baseUrl || 'https://api.encypher.com',
      accessToken: options.apiKey,
    });

    this.signing = new SigningApi(this.config);
    this.verification = new VerificationApi(this.config);
  }

  async sign(request: UnifiedSignRequest) {
    return this.signing.signContentApiV1SignPost({ unifiedSignRequest: request });
  }

  async verify(request: VerifyRequest) {
    return this.verification.verifyTextApiV1VerifyPost({ verifyRequest: request });
  }
}

// Re-export everything
export * from './apis';
export * from './models';
export * from './runtime';
