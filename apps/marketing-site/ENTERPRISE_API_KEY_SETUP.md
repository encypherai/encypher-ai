# Marketing Site Enterprise API Key Setup

## Overview

The marketing site's `/tools/encode-decode` page requires an Enterprise API key to proxy signing and verification requests through server-side routes (`/api/tools/sign` and `/api/tools/verify`).

## Production API Key

**Key Name:** `ency_marketing_site_prod_2026`

**Organization:** Encypher Corporation - Marketing Site  
**Tier:** Starter (Free)  
**Permissions:** `sign`, `verify` (basic operations only)  
**Monthly Limit:** 50,000 requests

### Key Configuration

This key is configured in `enterprise_api/app/dependencies.py` with the following settings:

```python
"ency_marketing_site_prod_2026": {
    "organization_id": "org_encypher_marketing",
    "organization_name": "Encypher Corporation - Marketing Site",
    "tier": "starter",
    "is_demo": False,  # Production key
    "features": {
        "team_management": False,
        "audit_logs": False,
        "merkle_enabled": False,
        "bulk_operations": False,
        "sentence_tracking": False,
        "streaming": False,
        "byok": False,
        "sso": False,
        "custom_assertions": False,
        "max_team_members": 1,
    },
    "permissions": ["sign", "verify"],
    "monthly_api_limit": 50000,
}
```

## Local Development Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. The key is already configured in `.env.example`:
   ```bash
   ENTERPRISE_API_KEY=ency_marketing_site_prod_2026
   ```

3. Restart your Next.js dev server:
   ```bash
   npm run dev
   ```

## Production Deployment (Railway)

### Set Environment Variable

Use Railway CLI to set the production environment variable:

```bash
# Login to Railway
npx @railway/cli login

# Link to your project
npx @railway/cli link

# Set the environment variable
npx @railway/cli variables set ENTERPRISE_API_KEY=ency_marketing_site_prod_2026
```

Or set it via Railway Dashboard:
1. Go to your marketing-site service
2. Navigate to **Variables** tab
3. Add new variable:
   - **Name:** `ENTERPRISE_API_KEY`
   - **Value:** `ency_marketing_site_prod_2026`
4. Redeploy the service

### Verify Configuration

After deployment, test the tools page:
- Visit: `https://encypherai.com/tools/encode-decode`
- Try encoding some text
- Verify it works without "Missing ENTERPRISE_API_KEY" error

## Security Notes

1. **Server-Side Only:** This key is only used in Next.js API routes (server-side), never exposed to the browser
2. **Rate Limited:** 50,000 requests/month limit prevents abuse
3. **Minimal Permissions:** Only `sign` and `verify` - no advanced features
4. **Starter Tier:** Free tier with basic functionality only
5. **Not a Secret:** This key is designed for public tool usage and is safe to commit to the repository

## Monitoring

Monitor usage via Enterprise API logs:
- Organization ID: `org_encypher_marketing`
- Check monthly usage against 50,000 limit
- Set up alerts if approaching limit

## Future Considerations

If the marketing site tools become heavily used:
1. Consider upgrading to Professional tier for higher limits
2. Implement client-side rate limiting
3. Add CAPTCHA for abuse prevention
4. Create separate keys for different tool pages

## Troubleshooting

### Error: "Missing ENTERPRISE_API_KEY"
- Verify `.env` file exists with `ENTERPRISE_API_KEY=ency_marketing_site_prod_2026`
- Restart Next.js dev server after adding the variable
- In production, verify Railway environment variable is set

### Error: "Quota exceeded"
- Check monthly usage in Enterprise API logs
- Consider upgrading tier or increasing limit
- Implement rate limiting on frontend

### Error: "Invalid API key"
- Verify the key matches exactly: `ency_marketing_site_prod_2026`
- Check Enterprise API is running and has the key configured in `dependencies.py`
- Verify `ENTERPRISE_API_URL` points to correct endpoint
