/**
 * Settings page JavaScript for Encypher Provenance plugin.
 * Handles connection testing and dynamic UI updates.
 */
(function($) {
    'use strict';

    const EncypherSettings = {
        init() {
            this.bindEvents();
            this.applyTierConstraints();
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

            $('#encypher-signing-mode').on('change', (event) => {
                this.toggleSigningProfileField(event.target.value);
            });
        },

        async checkConnection() {
            const $status = $('#connection-status');
            const apiUrl = $('input[name="encypher_assurance_settings[api_base_url]"]').val();

            if (!apiUrl) {
                $status.html('<span class="status-indicator dashicons dashicons-minus"></span> <span>No API URL configured</span>');
                return;
            }

            $status.html('<span class="status-indicator dashicons dashicons-update status-checking"></span> <span>Checking...</span>');

            try {
                // Use server-side check via WordPress REST API
                const response = await fetch(wpApiSettings.root + 'encypher-provenance/v1/test-connection', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': wpApiSettings.nonce
                    }
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    $status.html('<span class="status-indicator dashicons dashicons-yes-alt"></span> <span class="status-text-success">Connected</span>');
                } else {
                    $status.html('<span class="status-indicator dashicons dashicons-dismiss"></span> <span class="status-text-error">Not connected</span>');
                }
            } catch (error) {
                $status.html('<span class="status-indicator dashicons dashicons-dismiss"></span> <span class="status-text-error">Check failed</span>');
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

            // Get current form values (not saved settings)
            const apiBaseUrl = $('#api_base_url').val();
            const apiKey = $('#api_key').val();

            try {
                // Use WordPress REST API endpoint (server-side test)
                const response = await fetch(wpApiSettings.root + 'encypher-provenance/v1/test-connection', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': wpApiSettings.nonce
                    },
                    body: JSON.stringify({
                        api_base_url: apiBaseUrl,
                        api_key: apiKey
                    })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.message || 'Connection test failed');
                }

                // Build success message
                let message = '<div class="notice notice-success"><p><strong>Connection successful!</strong></p>';
                message += '<ul style="margin-left: 20px;">';
                message += `<li><strong>API URL:</strong> ${data.api_url}</li>`;
                message += `<li><strong>API Status:</strong> ${data.health?.status || 'OK'}</li>`;
                message += `<li><strong>API Key:</strong> ${data.api_key_configured ? 'Configured' : 'Not configured (using demo mode)'}</li>`;
                
                if (data.auth_note) {
                    message += `<li><strong>Note:</strong> ${data.auth_note}</li>`;
                }
                
                if (data.organization) {
                    message += `<li><strong>Organization:</strong> ${data.organization.name || data.organization.organization_id}</li>`;
                    if (data.organization.tier) {
                        message += `<li><strong>Tier:</strong> ${data.organization.tier}</li>`;
                    }
                }
                
                message += '</ul></div>';
                $result.html(message);

                // Update connection status indicator
                this.checkConnection();

            } catch (error) {
                $result.html(`<div class="notice notice-error"><p><strong>Connection failed:</strong> ${error.message}</p></div>`);
            } finally {
                $btn.prop('disabled', false).text('Test Connection');
            }
        },

        applyTierConstraints() {
            const data = this.getData();
            const tier = data.tier || 'starter';
            const $modeSelect = $('#encypher-signing-mode');

            if (!$modeSelect.length) {
                return;
            }

            if (tier === 'starter') {
                $modeSelect.prop('disabled', true);
                this.toggleSigningProfileField('managed');
                if (data.strings && data.strings.byokDisabled) {
                    this.renderInlineNotice($modeSelect, data.strings.byokDisabled, 'notice-warning');
                }
                return;
            }

            this.toggleSigningProfileField($modeSelect.val());
        },

        toggleSigningProfileField(mode) {
            const $profileField = $('#encypher-signing-profile-id');
            if (!$profileField.length) {
                return;
            }

            if (!$profileField.data('placeholder')) {
                $profileField.data('placeholder', $profileField.attr('placeholder'));
            }

            if (mode === 'byok') {
                $profileField.prop('disabled', false);
            } else {
                $profileField.prop('disabled', true);
            }
        },

        renderInlineNotice($sourceEl, message, noticeClass = 'notice-info') {
            if (!$sourceEl || !$sourceEl.length || !message) {
                return;
            }

            const $container = $sourceEl.closest('td');
            if (!$container.length) {
                return;
            }

            const $existing = $container.find('.encypher-inline-notice');
            if ($existing.length) {
                $existing.find('p').text(message);
                return;
            }

            const $notice = $('<div/>', {
                class: `notice ${noticeClass} encypher-inline-notice`,
                style: 'margin-top:8px;',
            }).append($('<p/>').text(message));

            $container.append($notice);
        },

        getData() {
            return window.EncypherSettingsData || {};
        }
    };

    // Initialize when document is ready
    $(document).ready(() => {
        EncypherSettings.init();
    });

})(jQuery);
