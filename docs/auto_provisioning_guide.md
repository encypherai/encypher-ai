# Auto-Provisioning Guide

**Automatic Organization and API Key Creation**

This guide explains how external services (SDK, WordPress plugin, CLI, mobile apps) can automatically provision organizations and obtain API keys without manual intervention.

---

## Overview

The auto-provisioning system allows external services to:
1. **Automatically create organizations** for new users
2. **Generate API keys** for authentication
3. **Set up user accounts** with appropriate permissions
4. **Configure tier-based features** and quotas

### Use Cases

- **SDK Initialization:** Auto-create account on first SDK use
- **WordPress Plugin:** Auto-provision on plugin activation
- **CLI Tool:** Auto-create account on first login
- **Mobile App:** Auto-provision during onboarding
- **Third-party Integrations:** Seamless account creation

---

## Quick Start

### 1. Auto-Provision Endpoint

**Endpoint:** `POST /api/v1/provisioning/auto-provision`

**Request:**
```json
{
  "email": "developer@example.com",
  "organization_name": "Example Corp",
  "source": "wordpress",
  "source_metadata": {
    "plugin_version": "1.2.3",
    "site_url": "https://example.com",
    "wordpress_version": "6.4"
  },
  "tier": "free",
  "auto_activate": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Organization and API key created successfully",
  "organization_id": "org_abc123",
  "organization_name": "Example Corp",
  "user_id": "user_xyz789",
  "api_key": {
    "api_key": "ency_live_1234567890abcdef",
    "key_id": "key_abc123",
    "organization_id": "org_abc123",
    "tier": "free",
    "created_at": "2024-10-28T12:00:00Z",
    "expires_at": null
  },
  "tier": "free",
  "features_enabled": {
    "merkle_trees": false,
    "bulk_operations": false,
    "advanced_analytics": false
  },
  "quota_limits": {
    "api_calls_per_month": 1000,
    "merkle_encoding_per_month": 0
  },
  "next_steps": {
    "documentation": "https://docs.encypher.ai/getting-started",
    "api_reference": "https://docs.encypher.ai/api",
    "upgrade": "https://encypher.ai/pricing"
  }
}
```

---

## Integration Examples

### WordPress Plugin

```php
<?php
/**
 * Auto-provision Encypher account on plugin activation
 */
function encypher_activate_plugin() {
    $admin_email = get_option('admin_email');
    $site_name = get_bloginfo('name');
    
    $response = wp_remote_post('https://api.encypher.ai/api/v1/provisioning/auto-provision', [
        'headers' => [
            'Content-Type' => 'application/json',
        ],
        'body' => json_encode([
            'email' => $admin_email,
            'organization_name' => $site_name,
            'source' => 'wordpress',
            'source_metadata' => [
                'plugin_version' => ENCYPHER_VERSION,
                'site_url' => get_site_url(),
                'wordpress_version' => get_bloginfo('version'),
            ],
            'tier' => 'free',
            'auto_activate' => true,
        ]),
    ]);
    
    if (is_wp_error($response)) {
        error_log('Encypher provisioning failed: ' . $response->get_error_message());
        return;
    }
    
    $body = json_decode(wp_remote_retrieve_body($response), true);
    
    if ($body['success']) {
        // Store API key
        update_option('encypher_api_key', $body['api_key']['api_key']);
        update_option('encypher_organization_id', $body['organization_id']);
        
        // Show success message
        add_action('admin_notices', function() use ($body) {
            echo '<div class="notice notice-success"><p>';
            echo 'Encypher activated! Your API key has been generated.';
            echo '</p></div>';
        });
    }
}

register_activation_hook(__FILE__, 'encypher_activate_plugin');
```

### Python SDK

```python
import requests
import os
from pathlib import Path

class EncypherClient:
    """Encypher SDK with auto-provisioning."""
    
    def __init__(self, email: str = None, api_key: str = None):
        """
        Initialize Encypher client.
        
        If no API key provided, auto-provisions one using email.
        """
        self.api_key = api_key or self._get_or_create_api_key(email)
        self.base_url = "https://api.encypher.ai"
    
    def _get_or_create_api_key(self, email: str) -> str:
        """Get existing API key or auto-provision new one."""
        # Check for stored API key
        config_file = Path.home() / '.encypher' / 'config.json'
        if config_file.exists():
            import json
            with open(config_file) as f:
                config = json.load(f)
                if 'api_key' in config:
                    return config['api_key']
        
        # Auto-provision
        if not email:
            raise ValueError("Email required for auto-provisioning")
        
        response = requests.post(
            f"{self.base_url}/api/v1/provisioning/auto-provision",
            json={
                "email": email,
                "source": "sdk",
                "source_metadata": {
                    "sdk_version": "1.0.0",
                    "platform": "python"
                },
                "tier": "free",
                "auto_activate": True
            }
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Store API key
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump({
                'api_key': data['api_key']['api_key'],
                'organization_id': data['organization_id']
            }, f)
        
        print(f"✓ Encypher account created for {email}")
        print(f"  Organization: {data['organization_name']}")
        print(f"  Tier: {data['tier']}")
        
        return data['api_key']['api_key']

# Usage
client = EncypherClient(email="developer@example.com")
```

### JavaScript/Node.js SDK

```javascript
const axios = require('axios');
const fs = require('fs');
const os = require('os');
const path = require('path');

class EncypherClient {
  constructor(options = {}) {
    this.apiKey = options.apiKey || this.getOrCreateApiKey(options.email);
    this.baseUrl = 'https://api.encypher.ai';
  }
  
  async getOrCreateApiKey(email) {
    // Check for stored API key
    const configPath = path.join(os.homedir(), '.encypher', 'config.json');
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      if (config.api_key) {
        return config.api_key;
      }
    }
    
    // Auto-provision
    if (!email) {
      throw new Error('Email required for auto-provisioning');
    }
    
    const response = await axios.post(
      `${this.baseUrl}/api/v1/provisioning/auto-provision`,
      {
        email,
        source: 'sdk',
        source_metadata: {
          sdk_version: '1.0.0',
          platform: 'nodejs'
        },
        tier: 'free',
        auto_activate: true
      }
    );
    
    const data = response.data;
    
    // Store API key
    const configDir = path.dirname(configPath);
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }
    
    fs.writeFileSync(configPath, JSON.stringify({
      api_key: data.api_key.api_key,
      organization_id: data.organization_id
    }, null, 2));
    
    console.log(`✓ Encypher account created for ${email}`);
    console.log(`  Organization: ${data.organization_name}`);
    console.log(`  Tier: ${data.tier}`);
    
    return data.api_key.api_key;
  }
}

// Usage
const client = new EncypherClient({ email: 'developer@example.com' });
```

### CLI Tool

```bash
#!/bin/bash
# encypher-cli auto-provision

EMAIL=$1

if [ -z "$EMAIL" ]; then
    echo "Usage: encypher-cli provision <email>"
    exit 1
fi

# Check for existing API key
CONFIG_FILE="$HOME/.encypher/config.json"
if [ -f "$CONFIG_FILE" ]; then
    API_KEY=$(jq -r '.api_key' "$CONFIG_FILE")
    if [ "$API_KEY" != "null" ]; then
        echo "✓ Already provisioned"
        echo "  API Key: ${API_KEY:0:20}..."
        exit 0
    fi
fi

# Auto-provision
echo "Provisioning Encypher account for $EMAIL..."

RESPONSE=$(curl -s -X POST https://api.encypher.ai/api/v1/provisioning/auto-provision \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$EMAIL\",
        \"source\": \"cli\",
        \"source_metadata\": {
            \"cli_version\": \"1.0.0\"
        },
        \"tier\": \"free\",
        \"auto_activate\": true
    }")

# Parse response
API_KEY=$(echo "$RESPONSE" | jq -r '.api_key.api_key')
ORG_ID=$(echo "$RESPONSE" | jq -r '.organization_id')
ORG_NAME=$(echo "$RESPONSE" | jq -r '.organization_name')

# Store config
mkdir -p "$(dirname "$CONFIG_FILE")"
echo "{\"api_key\": \"$API_KEY\", \"organization_id\": \"$ORG_ID\"}" > "$CONFIG_FILE"

echo "✓ Encypher account created"
echo "  Email: $EMAIL"
echo "  Organization: $ORG_NAME"
echo "  API Key: ${API_KEY:0:20}..."
```

---

## API Reference

### POST /api/v1/provisioning/auto-provision

Auto-provision an organization and API key.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | User email address |
| `organization_name` | string | No | Organization name (auto-generated if not provided) |
| `source` | string | Yes | Source of request (api/sdk/wordpress/cli/dashboard/mobile_app) |
| `source_metadata` | object | No | Additional metadata from source |
| `tier` | string | No | Initial tier (free/professional/enterprise), default: free |
| `auto_activate` | boolean | No | Auto-activate organization, default: true |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether provisioning succeeded |
| `message` | string | Success or error message |
| `organization_id` | string | Created organization ID |
| `organization_name` | string | Organization name |
| `user_id` | string | Created user ID |
| `api_key` | object | Generated API key details |
| `tier` | string | Organization tier |
| `features_enabled` | object | Enabled features |
| `quota_limits` | object | Quota limits |
| `next_steps` | object | Documentation links |

**Status Codes:**
- `201` - Created successfully
- `400` - Invalid request
- `429` - Rate limit exceeded
- `500` - Server error

---

## Security

### API Key Format

API keys follow this format:
```
ency_live_{40_character_random_string}
```

Example: `ency_live_1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r`

### Best Practices

1. **Store Securely:** Never commit API keys to version control
2. **Use Environment Variables:** Store in `.env` files or environment
3. **Rotate Regularly:** Generate new keys periodically
4. **Revoke Compromised Keys:** Immediately revoke if exposed
5. **Use HTTPS:** Always use HTTPS for API requests

### Rate Limits

- **10 requests/minute per IP**
- **100 requests/hour per email**
- **1000 requests/day per organization**

---

## Idempotency

The auto-provision endpoint is **idempotent**:
- If organization already exists for email, returns existing organization
- Generates a new API key each time
- Safe to call multiple times

---

## Error Handling

### Common Errors

**400 Bad Request:**
```json
{
  "detail": "Invalid email format"
}
```

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to provision organization"
}
```

### Retry Logic

Implement exponential backoff for retries:
```python
import time

def auto_provision_with_retry(email, max_retries=3):
    for attempt in range(max_retries):
        try:
            return auto_provision(email)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)
```

---

## Monitoring

### Provisioning Events

All provisioning events are logged with:
- Email address
- Source (sdk/wordpress/cli/etc)
- Timestamp
- Organization ID
- Success/failure status

### Webhooks

Configure webhooks to receive provisioning events:

```json
{
  "event_type": "organization.created",
  "event_id": "evt_abc123",
  "timestamp": "2024-10-28T12:00:00Z",
  "data": {
    "organization_id": "org_abc123",
    "email": "developer@example.com",
    "source": "wordpress",
    "tier": "free"
  }
}
```

---

## Testing

### Test Endpoint

Use test mode for development:

```bash
curl -X POST https://api.encypher.ai/api/v1/provisioning/auto-provision \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "source": "sdk",
    "tier": "free"
  }'
```

### Mock Responses

For local development, mock the provisioning response:

```javascript
// Mock for testing
const mockProvisionResponse = {
  success: true,
  organization_id: 'org_test123',
  api_key: {
    api_key: 'ency_test_mockkey123',
    key_id: 'key_test123'
  }
};
```

---

## Migration Guide

### Existing Users

If you have existing users, migrate them:

```python
# Migrate existing user to auto-provisioning
async def migrate_user(email, existing_org_id):
    # Create API key for existing org
    response = await create_api_key(
        organization_id=existing_org_id,
        email=email
    )
    return response['api_key']
```

---

## Support

### Documentation
- **Getting Started:** https://docs.encypher.ai/getting-started
- **API Reference:** https://docs.encypher.ai/api
- **SDK Guides:** https://docs.encypher.ai/sdk

### Contact
- **Email:** support@encypher.ai
- **Discord:** https://discord.gg/encypher
- **GitHub:** https://github.com/encypher/sdk

---

*Last Updated: 2025-10-28*  
*Version: 1.0.0*
