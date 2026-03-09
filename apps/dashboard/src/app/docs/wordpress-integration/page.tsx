import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { WordPressIntegrationGuideClient } from './WordPressIntegrationGuideClient';

export const dynamic = 'force-dynamic';

const GUIDE_CONTENT = `# WordPress Plugin Installation Guide

Install the Encypher Provenance plugin to automatically sign all your WordPress content with C2PA-compliant provenance markers and machine-readable licensing terms.

## What You'll Get

After installation, your WordPress site will:

- **Automatically sign new posts** with invisible C2PA provenance markers
- **Embed your licensing terms** (Bronze/Silver/Gold tiers) into every article
- **Display verification badges** so readers can verify content authenticity
- **Bulk sign your archive** to protect existing content
- **Provide court-admissible proof** of authorship and publication date

---

## Prerequisites

Before you begin, make sure you have:

1. **An Encypher account** - [Sign up here](https://dashboard.encypherai.com/signup) if you don't have one
2. **An API key** - Generate one from the [API Keys](/api-keys) page
3. **WordPress 5.0+** with admin access
4. **PHP 7.4+** (WordPress default)

---

## Step 1: Download the Plugin

Download the Encypher Provenance plugin from your dashboard:

1. Go to [Integrations](/integrations) in your Encypher dashboard
2. Find **WordPress** and click **Download plugin**
3. Save the \`encypher-provenance.zip\` file to your computer

![Download plugin from dashboard](/assets/docs/wordpress/step1-download.png)

---

## Step 2: Install in WordPress

### Option A: Upload via WordPress Admin

1. Log in to your WordPress admin panel
2. Go to **Plugins → Add New**
3. Click **Upload Plugin** at the top
4. Choose the \`encypher-provenance.zip\` file you downloaded
5. Click **Install Now**
6. After installation, click **Activate Plugin**

![Upload plugin in WordPress](/assets/docs/wordpress/step2-upload.png)

### Option B: Manual Installation (FTP/SFTP)

1. Extract the \`encypher-provenance.zip\` file
2. Upload the \`encypher-provenance\` folder to \`/wp-content/plugins/\`
3. Go to **Plugins** in WordPress admin
4. Find "Encypher Provenance" and click **Activate**

---

## Step 3: Configure Your API Key

1. After activation, go to **Settings → Encypher Provenance**
2. Enter your **API Key** from the [API Keys](/api-keys) page
3. Enter your **Organization ID** (found in [Settings](/settings))
4. Click **Save Changes**
5. Click **Test Connection** to verify

![Configure API key](/assets/docs/wordpress/step3-api-key.png)

> **Tip**: Your Organization ID looks like \`org_abc123xyz\` and can be found in your dashboard settings.

---

## Step 4: Configure Signing Options

The plugin offers several signing options:

| Option | Description | Recommended |
|--------|-------------|-------------|
| **Auto-sign new posts** | Automatically sign posts when published | ✅ Yes |
| **Auto-sign on update** | Re-sign posts when edited | ✅ Yes |
| **Attach Rights Profile** | Embed your licensing terms | ✅ Yes |
| **Include metadata** | Sign title, author, date | ✅ Yes |

### Enable Rights Profile

1. Make sure you've set up your [Rights Profile](/rights) in the dashboard first
2. In WordPress, enable **Attach Rights Profile**
3. This embeds your Bronze/Silver/Gold licensing terms into every signed article

![Signing options](/assets/docs/wordpress/step4-options.png)

---

## Step 5: Configure the Verification Badge

The verification badge lets readers verify your content's authenticity:

### Badge Position

- **Bottom of content** - Appears after the article (default)
- **Top of content** - Appears before the article
- **Floating bottom-right** - Fixed position badge

### Badge Appearance

- **Style**: Minimal, Standard, or Detailed
- **Theme**: Auto (matches site), Light, or Dark

![Badge settings](/assets/docs/wordpress/step5-badge.png)

---

## Step 6: Bulk Sign Your Archive

To sign your existing posts:

1. Go to **Encypher → Bulk Sign** in WordPress admin
2. Select post types to sign (Posts, Pages, etc.)
3. Review the archive count and estimated cost
4. Click **Start Bulk Signing**

The plugin processes posts in batches and shows real-time progress.

![Bulk signing interface](/assets/docs/wordpress/step6-bulk-sign.png)

### Archive Pricing

- **Free tier**: 1,000 documents/month included
- **Archive backfill**: $0.01/document (one-time)
- **Enterprise**: Unlimited signing included

---

## Verification: Test Your Setup

After installation, verify everything works:

### 1. Create a Test Post

1. Create a new post in WordPress
2. Add some text content
3. Publish the post

### 2. Check Signing Status

1. View the post on your site
2. Look for the verification badge
3. Click the badge to see provenance details

### 3. Verify via API

\`\`\`bash
curl -X POST https://api.encypherai.com/api/v1/verify \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"content": "Paste your signed article text here..."}'
\`\`\`

---

## Content Inventory

Track which posts are signed:

1. Go to **Encypher → Content Inventory**
2. Filter by signing status (Signed, Unsigned, Failed)
3. Click any post to view its provenance details

![Content inventory](/assets/docs/wordpress/step7-inventory.png)

---

## Troubleshooting

### "Connection Failed" Error

- Verify your API key is correct
- Check that your Organization ID matches your account
- Ensure your server can make outbound HTTPS requests

### Posts Not Being Signed

- Check that **Auto-sign new posts** is enabled
- Verify the post type is enabled for signing
- Check the error log in **Encypher → Logs**

### Badge Not Showing

- Clear your WordPress cache
- Check that the badge is enabled in settings
- Verify the post is actually signed (check Content Inventory)

### Bulk Signing Stops

- The plugin automatically resumes - just click Start again
- Check server error logs for PHP memory issues
- Contact support if issues persist

---

## Advanced Configuration

### Exclude Specific Posts

Add this to your theme's \`functions.php\`:

\`\`\`php
// Exclude specific posts from auto-signing
add_filter('encypher_should_sign_post', function($should_sign, $post_id) {
    $excluded = [123, 456]; // Post IDs to exclude
    return !in_array($post_id, $excluded) ? $should_sign : false;
}, 10, 2);
\`\`\`

### Custom Badge Placement

\`\`\`php
// Place badge manually in your theme
<?php if (function_exists('encypher_verification_badge')) {
    echo encypher_verification_badge(get_the_ID());
} ?>
\`\`\`

### Programmatic Signing

\`\`\`php
// Sign content programmatically
$signed_content = encypher_sign_text($content, [
    'title' => 'My Article',
    'use_rights_profile' => true
]);
\`\`\`

---

## FAQ

### Does signing affect SEO?

No. The provenance markers are invisible Unicode characters that don't affect how search engines index your content.

### Can I sign posts retroactively?

Yes! Use the Bulk Sign feature to sign your entire archive.

### What happens if I deactivate the plugin?

Your content keeps its embedded signatures. The verification badges will stop displaying, but the provenance data remains in your posts.

### Is there a performance impact?

Minimal. Signing happens during post save, adding ~100-200ms. Verification badges load asynchronously.

---

## Support

Need help? Contact us:

- **Email**: support@encypherai.com
- **Documentation**: [Publisher Integration Guide](/docs/publisher-integration)
- **API Reference**: [api.encypherai.com/docs](https://api.encypherai.com/docs)
`;

export default function WordPressIntegrationGuidePage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <WordPressIntegrationGuideClient markdown={GUIDE_CONTENT} />
      </div>
    </DashboardLayout>
  );
}
