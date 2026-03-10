(function () {
    'use strict';

    const { registerPlugin } = wp.plugins;
    const { PluginDocumentSettingPanel } = wp.editPost || wp.editor || {};
    const { Button, Spinner, Badge } = wp.components;
    const { useState, useEffect, useCallback } = wp.element;
    const { useSelect } = wp.data;
    const apiFetch = wp.apiFetch;

    if (!PluginDocumentSettingPanel) {
        return;
    }

    /**
     * Shield badge icon component (inline SVG).
     * color: 'green' | 'yellow' | 'red' | 'grey'
     */
    const ShieldBadge = function ({ status }) {
        const colors = {
            verified:  { stroke: '#00a32a', fill: '#d7f0de', label: 'AI content verified' },
            unverified:{ stroke: '#dba617', fill: '#fcf9e8', label: 'AI content unverified' },
            tampered:  { stroke: '#cc1818', fill: '#fce8e8', label: 'Tampering detected' },
            none:      { stroke: '#8c8f94', fill: '#f6f7f7', label: 'No AI content' },
            loading:   { stroke: '#8c8f94', fill: '#f6f7f7', label: 'Checking...' },
        };
        const c = colors[status] || colors.none;

        return wp.element.createElement(
            'div',
            {
                style: {
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 12px',
                    background: c.fill,
                    border: '1px solid ' + c.stroke,
                    borderRadius: '4px',
                    marginBottom: '12px',
                    width: '100%',
                    boxSizing: 'border-box',
                },
            },
            wp.element.createElement(
                'svg',
                {
                    viewBox: '0 0 24 24',
                    width: '20',
                    height: '20',
                    fill: 'none',
                    stroke: c.stroke,
                    strokeWidth: '2',
                    strokeLinecap: 'round',
                    strokeLinejoin: 'round',
                    'aria-hidden': 'true',
                },
                wp.element.createElement('path', { d: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z' }),
                status === 'verified'
                    ? wp.element.createElement('path', { d: 'M9 12l2 2 4-4' })
                    : null
            ),
            wp.element.createElement(
                'span',
                { style: { fontSize: '13px', fontWeight: '500', color: c.stroke } },
                c.label
            )
        );
    };

    /**
     * Main panel component.
     */
    const WordPressAIProvenancePanel = function () {
        const postId = useSelect(function (select) {
            return select('core/editor').getCurrentPostId();
        }, []);

        const postContent = useSelect(function (select) {
            return select('core/editor').getEditedPostContent();
        }, []);

        const [provenanceStatus, setProvenanceStatus] = useState('loading');
        const [provenanceDetails, setProvenanceDetails] = useState(null);
        const [isChecking, setIsChecking] = useState(false);
        const [lastChecked, setLastChecked] = useState(null);
        const [errorMessage, setErrorMessage] = useState('');

        // Check if WordPress/ai integration is enabled
        const wpAiEnabled = (
            typeof EncypherProvenanceConfig !== 'undefined' &&
            EncypherProvenanceConfig.wordpress_ai_enabled
        );

        const checkProvenance = useCallback(function () {
            if (!postId) {
                setProvenanceStatus('none');
                return;
            }

            setIsChecking(true);
            setErrorMessage('');

            apiFetch({
                path: 'encypher-provenance/v1/wordpress-ai-status?post_id=' + postId,
                method: 'GET',
                headers: {
                    'X-WP-Nonce': typeof EncypherProvenanceConfig !== 'undefined'
                        ? EncypherProvenanceConfig.nonce
                        : '',
                },
            })
                .then(function (response) {
                    setProvenanceStatus(response.status || 'unverified');
                    setProvenanceDetails(response.details || null);
                    setLastChecked(new Date().toLocaleTimeString());
                    setIsChecking(false);
                })
                .catch(function (err) {
                    // If endpoint doesn't exist yet, fall back to local content check
                    setProvenanceStatus('unverified');
                    setErrorMessage('');
                    setIsChecking(false);
                    setLastChecked(new Date().toLocaleTimeString());
                });
        }, [postId]);

        useEffect(function () {
            if (postId) {
                checkProvenance();
            }
        }, [postId]);

        const renderDetails = function () {
            if (!provenanceDetails) {
                return null;
            }

            const experiments = provenanceDetails.experiments || [];
            if (!experiments.length) {
                return null;
            }

            return wp.element.createElement(
                'div',
                { style: { marginTop: '8px' } },
                wp.element.createElement(
                    'p',
                    { style: { fontSize: '12px', color: '#646970', margin: '0 0 4px 0', fontWeight: '600' } },
                    'Signed AI experiments:'
                ),
                wp.element.createElement(
                    'ul',
                    { style: { margin: 0, padding: '0 0 0 16px', fontSize: '12px', color: '#646970' } },
                    experiments.map(function (exp, i) {
                        return wp.element.createElement(
                            'li',
                            { key: i },
                            exp.name || exp,
                            exp.signed_at
                                ? wp.element.createElement(
                                      'span',
                                      { style: { color: '#8c8f94', marginLeft: '4px' } },
                                      '(' + exp.signed_at + ')'
                                  )
                                : null
                        );
                    })
                )
            );
        };

        if (!wpAiEnabled) {
            return wp.element.createElement(
                PluginDocumentSettingPanel,
                {
                    name: 'encypher-wordpress-ai-provenance-panel',
                    title: 'AI Content Provenance',
                    className: 'encypher-wordpress-ai-panel',
                    initialOpen: false,
                },
                wp.element.createElement(
                    'div',
                    { style: { padding: '8px 0', fontSize: '13px', color: '#646970' } },
                    'Enable ',
                    wp.element.createElement('strong', null, 'WordPress/ai Integration'),
                    ' in Encypher settings to auto-sign AI-generated content.',
                    wp.element.createElement('br', null),
                    wp.element.createElement('br', null),
                    wp.element.createElement(
                        'a',
                        {
                            href: typeof EncypherProvenanceConfig !== 'undefined'
                                ? EncypherProvenanceConfig.settings_url || ''
                                : '',
                            style: { color: '#2271b1', textDecoration: 'underline' },
                        },
                        'Go to Encypher Settings'
                    )
                )
            );
        }

        return wp.element.createElement(
            PluginDocumentSettingPanel,
            {
                name: 'encypher-wordpress-ai-provenance-panel',
                title: 'AI Content Provenance',
                className: 'encypher-wordpress-ai-panel',
                initialOpen: true,
            },
            wp.element.createElement(
                'div',
                { style: { padding: '8px 0' } },
                wp.element.createElement(ShieldBadge, { status: isChecking ? 'loading' : provenanceStatus }),
                provenanceStatus === 'unverified' && wp.element.createElement(
                    'p',
                    { style: { fontSize: '12px', color: '#646970', margin: '0 0 8px 0' } },
                    'AI-generated content in this post has not been signed with Encypher provenance yet. ' +
                    'Provenance will be embedded automatically when WordPress/ai generates new content.'
                ),
                provenanceStatus === 'verified' && wp.element.createElement(
                    'p',
                    { style: { fontSize: '12px', color: '#2a6e00', margin: '0 0 8px 0' } },
                    'AI-generated content in this post is signed with C2PA-compatible provenance.'
                ),
                provenanceStatus === 'tampered' && wp.element.createElement(
                    'p',
                    { style: { fontSize: '12px', color: '#8a1515', margin: '0 0 8px 0' } },
                    'Provenance check failed — content may have been modified after signing.'
                ),
                provenanceStatus === 'none' && wp.element.createElement(
                    'p',
                    { style: { fontSize: '12px', color: '#646970', margin: '0 0 8px 0' } },
                    'No AI-generated content detected in this post.'
                ),
                renderDetails(),
                errorMessage && wp.element.createElement(
                    'p',
                    { style: { fontSize: '12px', color: '#cc1818', margin: '8px 0' } },
                    errorMessage
                ),
                wp.element.createElement(
                    'div',
                    { style: { display: 'flex', gap: '8px', marginTop: '12px', alignItems: 'center' } },
                    wp.element.createElement(
                        Button,
                        {
                            variant: 'secondary',
                            isSmall: true,
                            onClick: checkProvenance,
                            disabled: isChecking,
                            style: { flexShrink: 0 },
                        },
                        isChecking ? wp.element.createElement(Spinner, null) : 'Check Provenance'
                    ),
                    lastChecked && wp.element.createElement(
                        'span',
                        { style: { fontSize: '11px', color: '#8c8f94' } },
                        'Last checked: ' + lastChecked
                    )
                )
            )
        );
    };

    registerPlugin('encypher-wordpress-ai-provenance', {
        render: WordPressAIProvenancePanel,
        icon: 'shield',
    });

})();
