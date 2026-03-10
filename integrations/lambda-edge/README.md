# Encypher CDN Provenance — Lambda@Edge

Lambda@Edge **viewer-response** handler that injects a `C2PA-Manifest-URL` response header on
image responses served through a CloudFront distribution. The handler looks up the canonical
image URL against the Encypher API and, on a match, adds the header so downstream clients can
discover and verify C2PA provenance metadata.

## CloudFront configuration

- **Runtime**: Node.js 18.x (ESM)
- **Event type**: viewer response
- **Memory**: 128 MB (default) is sufficient; increase to 256 MB if latency is a concern
- **Timeout**: 5 seconds recommended (handler uses a 3 s internal fetch timeout)

## Setting ENCYPHER_API_URL

Lambda@Edge functions do **not** support runtime environment variables — the value is baked in
at deploy time. Options:

1. **Replace the constant directly**: edit the `ENCYPHER_API_URL` line in
   `cdn-provenance-handler.mjs` before packaging.
2. **CDK / Terraform**: use a string-replace step in your build pipeline to inject the value.
3. **SSM at cold-start**: add AWS SDK SSM `getParameter` calls outside the handler (module
   scope) to fetch the URL once per Lambda container lifetime.

## Deployment steps

1. Package the function:
   ```bash
   npm run package
   # produces function.zip
   ```
2. Upload `function.zip` to a Lambda function in **us-east-1** with the Node.js 18.x runtime.
3. Publish a new Lambda version and copy the ARN (must be a versioned ARN, not `$LATEST`).
4. In your CloudFront distribution, associate the versioned ARN with the **viewer response**
   event for the relevant cache behavior.
5. Deploy the CloudFront distribution and verify `C2PA-Manifest-URL` appears on image responses.
