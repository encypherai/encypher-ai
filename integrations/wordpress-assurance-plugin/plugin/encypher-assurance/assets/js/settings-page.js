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
            let apiUrl = $('input[name="encypher_assurance_settings[api_base_url]"]').val();
            const apiKey = $('input[name="encypher_assurance_settings[api_key]"]').val();

            if (!apiUrl) {
                $status.html('<span class="status-indicator status-unknown">⚪</span> <span>No API URL configured</span>');
                return;
            }

            // Convert Docker internal URLs to localhost for browser access
            apiUrl = this.convertToLocalhostUrl(apiUrl);

            $status.html('<span class="status-indicator status-checking">🔄</span> <span>Checking connection...</span>');

            try {
                const response = await fetch(apiUrl.replace(/\/+$/, '') + '/health', {
                    method: 'GET',
                    headers: apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {}
                });

                if (response.ok) {
                    $status.html('<span class="status-indicator status-connected">✅</span> <span class="status-text-success">Connected to Enterprise API</span>');
                } else {
                    $status.html(`<span class="status-indicator status-error">❌</span> <span class="status-text-error">Connection failed (${response.status})</span>`);
                }
            } catch (error) {
                const errorMsg = error.message.includes('ERR_NAME_NOT_RESOLVED') 
                    ? 'Cannot resolve hostname - use localhost:9000 for local testing'
                    : 'Cannot reach API - check URL and network';
                $status.html(`<span class="status-indicator status-error">❌</span> <span class="status-text-error">${errorMsg}</span>`);
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
            let apiUrl = $('input[name="encypher_assurance_settings[api_base_url]"]').val();
            const apiKey = $('input[name="encypher_assurance_settings[api_key]"]').val();

            if (!apiUrl) {
                $result.html('<div class="notice notice-error"><p>Please enter an API URL first.</p></div>');
                return;
            }

            // Show original URL vs converted URL if different
            const originalUrl = apiUrl;
            apiUrl = this.convertToLocalhostUrl(apiUrl);
            const urlConverted = originalUrl !== apiUrl;

            $btn.prop('disabled', true).text('Testing...');
            
            let infoMsg = '<div class="notice notice-info"><p>Testing connection...';
            if (urlConverted) {
                infoMsg += `<br><small>Note: Converting ${originalUrl} to ${apiUrl} for browser access</small>`;
            }
            infoMsg += '</p></div>';
            $result.html(infoMsg);

            try {
                // Test health endpoint
                const healthResponse = await fetch(apiUrl.replace(/\/+$/, '') + '/health', {
                    method: 'GET',
                    headers: apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {}
                });

                if (!healthResponse.ok) {
                    throw new Error(`Health check failed: ${healthResponse.status}`);
                }

                const healthData = await healthResponse.json();

                // If API key provided, test authentication
                let authStatus = 'Not tested (no API key provided)';
                let orgInfo = null;

                if (apiKey) {
                    try {
                        const authResponse = await fetch(apiUrl.replace(/\/+$/, '') + '/auth/verify', {
                            method: 'GET',
                            headers: { 'Authorization': `Bearer ${apiKey}` }
                        });

                        if (authResponse.ok) {
                            const authData = await authResponse.json();
                            authStatus = '✅ Authenticated';
                            orgInfo = authData.organization || null;
                        } else {
                            authStatus = `❌ Authentication failed (${authResponse.status})`;
                        }
                    } catch (authError) {
                        authStatus = `❌ Authentication error: ${authError.message}`;
                    }
                }

                // Build success message
                let message = '<div class="notice notice-success"><p><strong>✅ Connection successful!</strong></p>';
                message += '<ul style="margin-left: 20px;">';
                message += `<li><strong>API Status:</strong> ${healthData.status || 'OK'}</li>`;
                message += `<li><strong>Authentication:</strong> ${authStatus}</li>`;
                
                if (orgInfo) {
                    message += `<li><strong>Organization:</strong> ${orgInfo.name || orgInfo.organization_id}</li>`;
                    message += `<li><strong>Tier:</strong> ${orgInfo.tier || 'Unknown'}</li>`;
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
