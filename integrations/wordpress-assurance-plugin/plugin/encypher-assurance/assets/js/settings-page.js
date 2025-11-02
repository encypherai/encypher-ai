/**
 * Settings page JavaScript for Encypher Assurance plugin.
 * Handles connection testing and dynamic UI updates.
 */
(function($) {
    'use strict';

    const EncypherSettings = {
        init() {
            this.bindEvents();
            this.checkConnection();
        },

        bindEvents() {
            $('#test-connection-btn').on('click', (e) => {
                e.preventDefault();
                this.testConnection();
            });

            // Auto-test connection when API settings change
            $('input[name="encypher_assurance_settings[api_base_url]"], input[name="encypher_assurance_settings[api_key]"]').on('change', () => {
                this.checkConnection();
            });
        },

        async checkConnection() {
            const $status = $('#connection-status');
            const apiUrl = $('input[name="encypher_assurance_settings[api_base_url]"]').val();

            if (!apiUrl) {
                $status.html('<span class="status-indicator status-unknown">⚪</span> <span>No API URL configured</span>');
                return;
            }

            $status.html('<span class="status-indicator status-checking">🔄</span> <span>Checking...</span>');

            try {
                // Use server-side check via WordPress REST API
                const response = await fetch(wpApiSettings.root + 'encypher-assurance/v1/test-connection', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': wpApiSettings.nonce
                    }
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    $status.html('<span class="status-indicator status-connected">✅</span> <span class="status-text-success">Connected</span>');
                } else {
                    $status.html('<span class="status-indicator status-error">❌</span> <span class="status-text-error">Not connected</span>');
                }
            } catch (error) {
                $status.html('<span class="status-indicator status-error">❌</span> <span class="status-text-error">Check failed</span>');
            }
        },

        convertToLocalhostUrl(url) {
            // Convert Docker internal URLs to localhost for browser testing
            // enterprise-api:8000 -> localhost:9000 (mapped port)
            if (url.includes('enterprise-api:8000')) {
                return url.replace('enterprise-api:8000', 'localhost:9000');
            }
            return url;
        },

        async testConnection() {
            const $btn = $('#test-connection-btn');
            const $result = $('#test-connection-result');

            $btn.prop('disabled', true).text('Testing...');
            $result.html('<div class="notice notice-info"><p>Testing connection via WordPress server...</p></div>');

            try {
                // Use WordPress REST API endpoint (server-side test)
                const response = await fetch(wpApiSettings.root + 'encypher-assurance/v1/test-connection', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': wpApiSettings.nonce
                    }
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.message || 'Connection test failed');
                }

                // Build success message
                let message = '<div class="notice notice-success"><p><strong>✅ Connection successful!</strong></p>';
                message += '<ul style="margin-left: 20px;">';
                message += `<li><strong>API URL:</strong> ${data.api_url}</li>`;
                message += `<li><strong>API Status:</strong> ${data.health?.status || 'OK'}</li>`;
                
                if (data.authenticated) {
                    message += `<li><strong>Authentication:</strong> ✅ Authenticated</li>`;
                    if (data.organization) {
                        message += `<li><strong>Organization:</strong> ${data.organization.name || data.organization.organization_id}</li>`;
                        if (data.organization.tier) {
                            message += `<li><strong>Tier:</strong> ${data.organization.tier}</li>`;
                        }
                    }
                } else if (data.auth_error) {
                    message += `<li><strong>Authentication:</strong> ❌ ${data.auth_error}</li>`;
                } else {
                    message += `<li><strong>Authentication:</strong> ${data.auth_note || 'Not tested'}</li>`;
                }
                
                message += '</ul></div>';
                $result.html(message);

                // Update connection status indicator
                this.checkConnection();

            } catch (error) {
                $result.html(`<div class="notice notice-error"><p><strong>❌ Connection failed:</strong> ${error.message}</p></div>`);
            } finally {
                $btn.prop('disabled', false).text('Test Connection');
            }
        }
    };

    // Initialize when document is ready
    $(document).ready(() => {
        EncypherSettings.init();
    });

})(jQuery);
