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
            this.resumeConnectPollingIfNeeded();
        },

        bindEvents() {
            $('#test-connection-btn').on('click', (e) => {
                e.preventDefault();
                this.testConnection();
            });

            // Auto-save + connect when API key is pasted
            let _quickConnectTimer = null;
            $('#api_key').on('paste', () => {
                this.showApiKeyStatus('saving', 'Verifying...');
                clearTimeout(_quickConnectTimer);
                // Delay slightly so the browser has updated the input value
                _quickConnectTimer = setTimeout(() => this.quickConnect(), 50);
            });

            // Re-verify when URL changes and a key is already present
            $('#api_base_url').on('change', () => {
                if ($('#api_key').val()) {
                    this.showApiKeyStatus('saving', 'Verifying...');
                    clearTimeout(_quickConnectTimer);
                    _quickConnectTimer = setTimeout(() => this.quickConnect(), 50);
                }
            });

            // Auto-test connection when API settings change
            $('input[name="encypher_provenance_settings[api_base_url]"], input[name="encypher_provenance_settings[api_key]"]').on('change', () => {
                this.updateChecklistProgress();
                this.checkConnection();
            });

            $('#encypher-signing-mode').on('change', (event) => {
                this.toggleSigningProfileField(event.target.value);
            });

            $('#encypher-connect-start-btn').on('click', (e) => {
                e.preventDefault();
                this.startMagicLinkConnect();
            });

            $('#encypher-connect-poll-btn').on('click', (e) => {
                e.preventDefault();
                this.pollMagicLinkConnect();
            });
        },

        async startMagicLinkConnect() {
            const email = $('#encypher-connect-email').val();
            const apiBaseUrl = $('#api_base_url').val();
            const $status = $('#encypher-connect-status');
            const $startBtn = $('#encypher-connect-start-btn');

            if (!email) {
                $status.html('<div class="notice notice-error"><p>Please enter a work email address.</p></div>');
                return;
            }

            $startBtn.prop('disabled', true).text('Sending...');
            $status.html('<div class="notice notice-info"><p>Sending your secure approval link…</p></div>');

            try {
                const response = await fetch(wpApiSettings.root + 'encypher-provenance/v1/connect/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': wpApiSettings.nonce
                    },
                    body: JSON.stringify({ email, api_base_url: apiBaseUrl })
                });

                const payload = await response.json();
                if (!response.ok || !payload.success) {
                    throw new Error(payload.message || payload.data?.message || 'Unable to start secure connect flow.');
                }

                const sessionId = payload.data?.session_id || '';
                $('input[name="encypher_provenance_settings[connect_email]"]').val(email);
                $('input[name="encypher_provenance_settings[connect_session_id]"]').val(sessionId);
                if (window.EncypherSettingsData) {
                    window.EncypherSettingsData.connectEmail = email;
                    window.EncypherSettingsData.connectSessionId = sessionId;
                }

                $('#encypher-connect-poll-btn').prop('disabled', false);
                $status.html(`<div class="notice notice-success"><p>${this.getData().strings?.connectStarted || 'Check your email for the secure approval link.'}</p></div>`);
                this.beginConnectPolling();
            } catch (error) {
                $status.html(`<div class="notice notice-error"><p>${error.message}</p></div>`);
            } finally {
                $startBtn.prop('disabled', false).text('Email me a secure connect link');
            }
        },

        async pollMagicLinkConnect() {
            const sessionId = $('input[name="encypher_provenance_settings[connect_session_id]"]').val() || this.getData().connectSessionId;
            const $status = $('#encypher-connect-status');

            if (!sessionId) {
                $status.html('<div class="notice notice-warning"><p>No pending secure connect session was found.</p></div>');
                return;
            }

            try {
                const response = await fetch(wpApiSettings.root + 'encypher-provenance/v1/connect/poll', {
                    method: 'GET',
                    headers: {
                        'X-WP-Nonce': wpApiSettings.nonce
                    }
                });
                const payload = await response.json();

                if (!response.ok || !payload.success) {
                    throw new Error(payload.message || payload.data?.message || 'Unable to check secure connect status.');
                }

                const data = payload.data || {};
                if (data.status === 'completed' && data.api_key) {
                    $('#api_key').val(data.api_key);
                    $('input[name="encypher_provenance_settings[connect_session_id]"]').val('');
                    $('input[name="encypher_provenance_settings[connect_email]"]').val('');
                    $('#encypher-connect-poll-btn').prop('disabled', true);
                    if (window.EncypherSettingsData) {
                        window.EncypherSettingsData.connectSessionId = '';
                        window.EncypherSettingsData.connectEmail = '';
                    }

                    this.showApiKeyStatus('saved', 'Provisioned automatically');
                    this.setChecklistStepState('api-key', true);
                    this.setChecklistStepState('connection-test', true);
                    this.updateChecklistProgress();
                    this.updateHealthCard({
                        state: 'connected',
                        stateLabel: 'Connected and ready',
                        apiUrl: data.api_base_url || $('#api_base_url').val(),
                        organization: data.organization_name || 'Connected workspace',
                        lastCheck: this.currentTimestamp(),
                    });
                    $status.html(`<div class="notice notice-success"><p>${this.getData().strings?.connectCompleted || 'WordPress connected successfully.'}</p></div>`);
                    this.stopConnectPolling();
                    return;
                }

                $status.html('<div class="notice notice-info"><p>Waiting for email approval. We will keep checking automatically.</p></div>');
            } catch (error) {
                $status.html(`<div class="notice notice-error"><p>${error.message}</p></div>`);
                this.stopConnectPolling();
            }
        },

        beginConnectPolling() {
            this.stopConnectPolling();
            this._connectPollTimer = window.setInterval(() => {
                this.pollMagicLinkConnect();
            }, 5000);
        },

        stopConnectPolling() {
            if (this._connectPollTimer) {
                window.clearInterval(this._connectPollTimer);
                this._connectPollTimer = null;
            }
        },

        resumeConnectPollingIfNeeded() {
            const sessionId = $('input[name="encypher_provenance_settings[connect_session_id]"]').val() || this.getData().connectSessionId;
            if (sessionId) {
                $('#encypher-connect-poll-btn').prop('disabled', false);
                this.beginConnectPolling();
            }
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
                    },
                    body: JSON.stringify({
                        api_base_url: apiUrl,
                        api_key: apiKey
                    })
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

        /**
         * Verify credentials and save them in one shot (triggered by paste).
         * Updates the health card and checklist with the returned org/tier info.
         */
        async quickConnect() {
            const apiBaseUrl = $('#api_base_url').val();
            const apiKey     = $('#api_key').val();

            if (!apiBaseUrl || !apiKey) {
                return;
            }

            try {
                const response = await fetch(wpApiSettings.root + 'encypher-provenance/v1/quick-connect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': wpApiSettings.nonce
                    },
                    body: JSON.stringify({ api_base_url: apiBaseUrl, api_key: apiKey })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    this.showApiKeyStatus('saved', 'Saved — connected');
                    this.setChecklistStepState('connection-test', true);
                    this.updateHealthCard({
                        state: 'connected',
                        stateLabel: 'Connected and ready',
                        apiUrl: data.api_url || apiBaseUrl,
                        tier: data.organization?.tier || data.tier || 'free',
                        organization: data.organization?.name || 'Not available',
                        lastCheck: this.currentTimestamp(),
                    });
                    this.updateChecklistProgress();
                    // Refresh tier constraints with new data
                    if (window.EncypherSettingsData) {
                        window.EncypherSettingsData.tier = data.tier || 'free';
                        this.applyTierConstraints();
                    }
                } else {
                    const msg = data.message || data.data?.message || 'Connection failed';
                    this.showApiKeyStatus('error', msg);
                    this.setChecklistStepState('connection-test', false);
                    this.updateChecklistProgress();
                }
            } catch (error) {
                this.showApiKeyStatus('error', error.message);
            }
        },

        /**
         * Show an inline status message next to the API key field.
         * state: 'saving' | 'saved' | 'error'
         */
        showApiKeyStatus(state, message) {
            let $status = $('#encypher-api-key-status');
            if (!$status.length) {
                $status = $('<span>', { id: 'encypher-api-key-status' });
                $('#api_key').after($status);
            }
            $status
                .removeClass('encypher-key-status-saving encypher-key-status-saved encypher-key-status-error')
                .addClass('encypher-key-status-' + state)
                .text(message);
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
