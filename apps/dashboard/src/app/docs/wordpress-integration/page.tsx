import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { WordPressIntegrationGuideClient } from './WordPressIntegrationGuideClient';

export const dynamic = 'force-dynamic';

const GUIDE_CONTENT = `# WordPress Plugin Installation Guide

Install the Encypher Provenance plugin to add standards-based proof of origin to your WordPress publishing workflow.

## What You'll Get

After installation, your WordPress site will:

- **Connect to your Encypher workspace** with a secure email-based approval flow
- **Automatically sign new and updated posts** with invisible C2PA provenance markers
- **Preserve provenance across edits** so the verification view reflects the content history
- **Display verification badges** so readers can check authenticity on the frontend
- **Bulk sign your archive** when you want older content covered too

---

## Prerequisites

Before you begin, make sure you have:

1. **An Encypher account** - [Sign up here](https://dashboard.encypher.com/signup) if you don't have one
2. **WordPress 6.0+** with admin access
3. **PHP 7.4+** (WordPress default)
4. **Access to your work email inbox** so you can approve the secure connection link

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
7. Open **Encypher → Settings** after activation to start configuration

![Upload plugin in WordPress](/assets/docs/wordpress/step2-upload.png)

### Option B: Manual Installation (FTP/SFTP)

1. Extract the \`encypher-provenance.zip\` file
2. Upload the \`encypher-provenance\` folder to \`/wp-content/plugins/\`
3. Go to **Plugins** in WordPress admin
4. Find "Encypher Provenance" and click **Activate**

After activation, open **Encypher → Settings** to connect the site to your Encypher workspace.

---

## Step 3: Connect Your Workspace

1. After activation, go to **Encypher → Settings**
2. Enter your **work email** and click **Email me a secure connect link**
3. Open the email from Encypher and approve the WordPress connection in your browser
4. Return to WordPress and keep the settings page open for a few seconds while the plugin polls for completion
5. Confirm the plugin shows the workspace as connected and that the API key was provisioned automatically

![Connect your workspace](/assets/docs/wordpress/step3-api-key.png)

> **Tip**: If your organization already manages Encypher credentials centrally, you can still paste an existing API key manually and use **Test Connection** to verify the setup.

### Manual API Key Fallback

1. Open [API Keys](/api-keys) in the Encypher dashboard
2. Create or copy an existing API key
3. Paste it into the plugin settings page
4. Click **Test Connection** to confirm the workspace metadata resolves correctly

---

## Step 4: Choose Your Signing Defaults

The plugin offers several signing options:

| Option | Description | Recommended |
|--------|-------------|-------------|
| **Auto-sign new posts** | Automatically sign posts when published | Yes |
| **Auto-sign on update** | Re-sign posts when edited | Yes |
| **Show verification badge** | Display a public authenticity badge on signed posts | Yes |
| **Metadata format** | Keep the default C2PA provenance wrapper enabled | Yes |

### Recommended defaults

1. Leave **Auto-sign new posts** enabled so published content is protected automatically
2. Leave **Auto-sign on update** enabled so edited content preserves its provenance chain
3. Keep **Metadata Format** on **C2PA** so the verification view exposes standards-based provenance details
4. Use **Test Connection** once before publishing your first post

![Signing options](/assets/docs/wordpress/step4-options.png)

---

## Step 5: Configure the Verification Badge

The verification badge lets readers verify your content's authenticity:

### Badge Position

- **Bottom of post** - Appears after the article, above comments (default)
- **Top of post** - Appears before the article
- **Bottom-right corner (floating)** - Fixed position badge in the corner

### Badge Visibility

- **Show C2PA badge** - Displays the badge on all C2PA-marked posts
- **Whitelabeling** - Uncheck to remove Encypher branding from public badges

![Badge settings](/assets/docs/wordpress/step5-badge.png)

---

## Step 6: Publish and Sign Your First Post

Use a normal WordPress post to confirm the plugin is connected and signing correctly.

1. Create a new post in WordPress
2. Publish the post with **Auto-sign new posts** enabled
3. Confirm the Encypher sidebar or post UI shows the content as signed
4. Make a quick edit and update the post once to confirm the provenance chain stays intact

After that first publish, your site is ready for broader rollout.

![Signed post in WordPress](/assets/docs/wordpress/step6-signed-post.png)

---

## Step 7: Bulk Sign Your Archive

To sign your existing posts:

1. Go to **Encypher → Bulk Sign** in WordPress admin
2. Select post types to sign (Posts, Pages, etc.)
3. Review the archive count
4. Click **Start Bulk Signing**

The plugin processes posts in batches and shows real-time progress.

![Bulk signing interface](/assets/docs/wordpress/step6-bulk-sign.png)

---

## Step 8: Verify on the Frontend

After installation, verify everything works:

### 1. Open a Signed Post

1. Open a signed post on the frontend
2. Confirm the article displays normally
3. Look for the verification badge near the article footer or page edge, depending on your chosen badge position

![Frontend verification badge on a signed post](/assets/docs/wordpress/frontend-badge.png)

### 2. Check Signing Status

1. View the post on your site
2. Look for the verification badge
3. Click the badge to see provenance details, signing status, and verification information

### 3. Verify in WordPress

1. Return to **Encypher → Analytics** or the relevant post screen in WordPress
2. Confirm the post appears as signed
3. Review the latest verification details and timestamps

---

## Step 9: Review Ongoing Coverage

After the first successful publish, use the plugin's WordPress surfaces to confirm the rollout is healthy:

1. Open **Encypher → Analytics** to review signing coverage and recent activity
2. Use **Encypher → Content** to inspect signed posts and confirm the latest content is protected
3. Return to **Encypher → Settings** if you need to retest the workspace connection
4. For multi-site teams, repeat the same flow for each WordPress property

![WordPress content coverage](/assets/docs/wordpress/step7-inventory.png)

---

## Troubleshooting

### "Connection Failed" Error

- Re-run **Email me a secure connect link** and approve the latest secure link
- If using manual credentials, verify your API key is correct
- Ensure your server can make outbound HTTPS requests

### Posts Not Being Signed

- Check that **Auto-sign new posts** is enabled
- Verify the post type is enabled for signing
- Check the error log in **Encypher → Logs**

### Badge Not Showing

- Clear your WordPress cache
- Check that the badge is enabled in settings
- Verify the post is actually signed (check Encypher → Content or Analytics)

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

### Does this support teams that already manage Encypher credentials centrally?

Yes. Secure email connect is the recommended path for first-time setup, but the plugin still supports pasting an existing Encypher API key manually.

### What happens if I deactivate the plugin?

Your content keeps its embedded signatures. The verification badges will stop displaying, but the provenance data remains in your posts.

### Is there a performance impact?

Minimal. Signing happens during post save, adding ~100-200ms. Verification badges load asynchronously.

---

## Support

Need help? Contact us:

- **Email**: support@encypher.com
- **Documentation**: [Publisher Integration Guide](/docs/publisher-integration)
- **API Reference**: [api.encypher.com/docs](https://api.encypher.com/docs)
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
