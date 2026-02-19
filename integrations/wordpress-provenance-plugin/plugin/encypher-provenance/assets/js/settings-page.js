/**
 * Settings page JavaScript for Encypher Provenance plugin.
 * Handles connection testing and dynamic UI updates.
 */
(function($) {
    'use strict';

    const HEALTH_COPY = {
        lastCheckLabel: 'Last check:',
    };

    const EncypherSettings = {
        init() {
            this.bindEvents();
            this.applyTierConstraints();
            this.checkConnection();
            this.updateChecklistProgress();
        },

        bindEvents() {
            $('#test-connection-btn').on('click', (e) => {
                e.preventDefault();
                this.testConnection();
            });

            // Auto-test connection when API settings change
            $('input[name="encypher_provenance_settings[api_base_url]"], input[name="encypher_provenance_settings[api_key]"]').on('change', () => {
                this.updateChecklistProgress();
                this.checkConnection();
            });

            $('#encypher-signing-mode').on('change', (event) => {
                this.toggleSigningProfileField(event.target.value);
            });
        },

        async checkConnection() {
            const $status = $('#connection-status');
            const apiUrl = $('input[name="encypher_provenance_settings[api_base_url]"]').val();
            const apiKey = $('input[name="encypher_provenance_settings[api_key]"]').val();

            this.setChecklistStepState('api-url', !!apiUrl);
            this.setChecklistStepState('api-key', !!apiKey);

            if (!apiUrl) {
                $status.html('<span class="status-indicator dashicons dashicons-minus"></span> <span>No API URL configured</span>');
                this.updateHealthCard({
                    state: 'disconnected',
                    stateLabel: 'Disconnected',
                    apiUrl,
                });
                this.setChecklistStepState('connection-test', false);
                this.updateChecklistProgress();
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
                    this.setChecklistStepState('connection-test', true);
                    this.updateHealthCard({
                        state: data.status || 'connected',
                        stateLabel: 'Connected and ready',
                        apiUrl: data.api_url || apiUrl,
                        tier: data.organization?.tier || 'free',
                        organization: data.organization?.name || data.organization?.organization_id || 'Not available',
                        lastCheck: this.currentTimestamp(),
                    });
                } else {
                    $status.html('<span class="status-indicator dashicons dashicons-dismiss"></span> <span class="status-text-error">Not connected</span>');
                    this.setChecklistStepState('connection-test', false);
                    this.updateHealthCard({
                        state: 'auth_required',
                        stateLabel: 'Auth required',
                        apiUrl,
                        lastCheck: this.currentTimestamp(),
                    });
                }
            } catch (error) {
                $status.html('<span class="status-indicator dashicons dashicons-dismiss"></span> <span class="status-text-error">Check failed</span>');
                this.setChecklistStepState('connection-test', false);
                this.updateHealthCard({
                    state: 'disconnected',
                    stateLabel: 'Disconnected',
                    apiUrl,
                    lastCheck: this.currentTimestamp(),
                });
            }

            this.updateChecklistProgress();
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
            const $status = $('#connection-status');

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

                // Update connection status indicator using the same unsaved values tested above.
                $status.html('<span class="status-indicator dashicons dashicons-yes-alt"></span> <span class="status-text-success">Connected</span>');
                this.setChecklistStepState('connection-test', true);
                this.updateChecklistProgress();

                this.updateHealthCard({
                    state: data.status || 'connected',
                    stateLabel: 'Connected and ready',
                    apiUrl: data.api_url || apiBaseUrl,
                    tier: data.organization?.tier || 'free',
                    organization: data.organization?.name || data.organization?.organization_id || 'Not available',
                    lastCheck: this.currentTimestamp(),
                });

            } catch (error) {
                $result.html(`<div class="notice notice-error"><p><strong>Connection failed:</strong> ${error.message}</p></div>`);
                $status.html('<span class="status-indicator dashicons dashicons-dismiss"></span> <span class="status-text-error">Not connected</span>');
                this.setChecklistStepState('connection-test', false);
                this.updateChecklistProgress();
                this.updateHealthCard({
                    state: 'disconnected',
                    stateLabel: 'Disconnected',
                    apiUrl: apiBaseUrl,
                    lastCheck: this.currentTimestamp(),
                });
            } finally {
                $btn.prop('disabled', false).text('Test Connection');
            }
        },

        setChecklistStepState(step, complete) {
            const $item = $(`#encypher-launch-checklist li[data-step="${step}"]`);
            if (!$item.length) {
                return;
            }

            $item.toggleClass('is-complete', !!complete);
            $item.toggleClass('is-pending', !complete);
        },

        updateChecklistProgress() {
            const $items = $('#encypher-launch-checklist li');
            if (!$items.length) {
                return;
            }

            const complete = $items.filter('.is-complete').length;
            $('#encypher-launch-progress').text(`${complete} of 3 launch steps complete`);
        },

        updateHealthCard(payload = {}) {
            const defaults = {
                state: 'unknown',
                stateLabel: 'No recent health check',
                apiUrl: '',
                tier: null,
                organization: null,
                lastCheck: null,
            };
            const data = { ...defaults, ...payload };

            const $state = $('#encypher-connection-health-state');
            if ($state.length) {
                $state.text(data.stateLabel);
            }

            if (data.apiUrl) {
                $('#encypher-connection-health-url').text(data.apiUrl);
            }

            if (data.tier) {
                $('#encypher-connection-health-tier').text(data.tier);
            }

            if (data.organization) {
                $('#encypher-connection-health-org').text(data.organization);
            }

            if (data.lastCheck) {
                $('#encypher-connection-health-last-check').text(data.lastCheck);
                $('#encypher-connection-health-last-check').attr('aria-label', `${HEALTH_COPY.lastCheckLabel} ${data.lastCheck}`);
            }

            const $statusField = $('input[name="encypher_provenance_settings[connection_last_status]"]');
            const $lastCheckedField = $('input[name="encypher_provenance_settings[connection_last_checked_at]"]');
            if ($statusField.length) {
                $statusField.val(data.state);
            }
            if ($lastCheckedField.length && data.lastCheck) {
                $lastCheckedField.val(data.lastCheck);
            }
        },

        currentTimestamp() {
            return new Date().toISOString();
        },

        applyTierConstraints() {
            const data = this.getData();
            const tier = data.tier || 'free';
            const $modeSelect = $('#encypher-signing-mode');

            if (!$modeSelect.length) {
                return;
            }

            if (tier === 'free') {
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
