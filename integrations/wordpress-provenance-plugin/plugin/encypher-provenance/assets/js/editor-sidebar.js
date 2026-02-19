(function () {
    const { registerPlugin } = wp.plugins;
    const editorSlotFills = wp.editPost || {};
    const wpEditorSlotFills = wp.editor || {};
    const PluginDocumentSettingPanel = wpEditorSlotFills.PluginDocumentSettingPanel || editorSlotFills.PluginDocumentSettingPanel;
    const PluginPrePublishPanel = wpEditorSlotFills.PluginPrePublishPanel || editorSlotFills.PluginPrePublishPanel;
    const { Button, Notice, Spinner } = wp.components;
    const { useState, useEffect } = wp.element;
    const { useSelect } = wp.data;
    const apiFetch = wp.apiFetch;

    const StatusPanel = function () {
        const postId = useSelect((select) => select('core/editor').getCurrentPostId(), []);
        const postStatus = useSelect((select) => select('core/editor').getEditedPostAttribute('status'), []);
        const [status, setStatus] = useState('loading');
        const [documentId, setDocumentId] = useState('');
        const [verificationUrl, setVerificationUrl] = useState('');
        const [totalSentences, setTotalSentences] = useState(null);
        const [lastSigned, setLastSigned] = useState('');
        const [showManifest, setShowManifest] = useState(false);
        const [manifestData, setManifestData] = useState(null);
        const [verifying, setVerifying] = useState(false);
        const [sentenceSegments, setSentenceSegments] = useState([]);
        const [sentencesTotal, setSentencesTotal] = useState(0);
        const [showAllSentences, setShowAllSentences] = useState(false);
        const tier = (typeof EncypherProvenanceConfig !== 'undefined' && EncypherProvenanceConfig.tier) ? EncypherProvenanceConfig.tier : 'free';
        const [usage, setUsage] = useState(
            (typeof EncypherProvenanceConfig !== 'undefined' && EncypherProvenanceConfig.usage && EncypherProvenanceConfig.usage.api_calls)
                ? EncypherProvenanceConfig.usage.api_calls
                : { used: 0, limit: 1000, remaining: 1000, percentage_used: 0, is_unlimited: false }
        );

        const renderBrandingPrimer = () => {
            const children = [
                wp.element.createElement(
                    'p',
                    { key: 'brand-copy', className: 'encypher-brand-copy' },
                    'Encypher powers this provenance workflow with C2PA-compatible signing and verification.'
                ),
            ];

            if (tier === 'free') {
                children.push(
                    wp.element.createElement(
                        'p',
                        { key: 'free-cap', className: 'encypher-plan-note' },
                        'Free plan includes up to 1,000 sign requests/month.'
                    )
                );
                children.push(
                    wp.element.createElement(
                        'p',
                        { key: 'free-overage', className: 'encypher-plan-note' },
                        '$0.02/sign request after the monthly cap.'
                    )
                );
                children.push(
                    wp.element.createElement(
                        'p',
                        { key: 'free-verify-soft-cap', className: 'encypher-plan-note' },
                        'Verification stays available with a soft cap of 10,000 requests/month.'
                    )
                );
                children.push(
                    wp.element.createElement(
                        'p',
                        { key: 'free-addons', className: 'encypher-plan-note' },
                        'Whitelabel and advanced controls are available as add-ons, or included with Enterprise.'
                    )
                );
            }

            return wp.element.createElement('div', { className: 'encypher-brand-banner' }, children);
        };

        const renderUsageMeter = () => {
            const used = Number.isFinite(Number(usage.used)) ? Number(usage.used) : 0;
            const isUnlimited = Boolean(usage.is_unlimited) || Number(usage.limit) < 0;
            const limit = isUnlimited ? -1 : (Number.isFinite(Number(usage.limit)) && Number(usage.limit) > 0 ? Number(usage.limit) : 1000);
            const remaining = isUnlimited
                ? -1
                : (Number.isFinite(Number(usage.remaining)) ? Math.max(0, Number(usage.remaining)) : Math.max(0, limit - used));
            const percentage = isUnlimited
                ? 0
                : Math.min(100, Math.max(0, Number.isFinite(Number(usage.percentage_used)) ? Number(usage.percentage_used) : ((used / limit) * 100)));

            return wp.element.createElement(
                'div',
                { className: 'encypher-usage-meter' },
                wp.element.createElement('h4', { className: 'encypher-section-title' }, 'Monthly API call usage'),
                isUnlimited
                    ? wp.element.createElement(
                          'p',
                          { className: 'encypher-usage-summary' },
                          'Monthly API calls this month: ',
                          wp.element.createElement('strong', null, used.toLocaleString()),
                          ' (Unlimited plan)'
                      )
                    : wp.element.createElement(
                          wp.element.Fragment,
                          null,
                          wp.element.createElement(
                              'p',
                              { className: 'encypher-usage-summary' },
                              'Monthly API calls this month: ',
                              wp.element.createElement('strong', null, used.toLocaleString()),
                              ' / ',
                              limit.toLocaleString(),
                              ' (',
                              Math.round(percentage),
                              '%)'
                          ),
                          wp.element.createElement(
                              'div',
                              { className: 'encypher-usage-track', role: 'progressbar', 'aria-valuemin': 0, 'aria-valuemax': 100, 'aria-valuenow': Math.round(percentage) },
                              wp.element.createElement('div', { className: 'encypher-usage-fill', style: { width: `${percentage}%` } })
                          ),
                          wp.element.createElement(
                              'p',
                              { className: 'encypher-usage-remaining' },
                              'API calls remaining this month: ',
                              wp.element.createElement('strong', null, remaining.toLocaleString())
                          )
                      )
            );
        };

        const fetchStatus = () => {
            if (!postId) {
                return;
            }
            setStatus('loading');
            apiFetch({
                path: `encypher-provenance/v1/status?post_id=${postId}`,
                method: 'GET',
                headers: {
                    'X-WP-Nonce': EncypherProvenanceConfig.nonce,
                },
            })
                .then((response) => {
                    setStatus(response.status || 'not_signed');
                    setDocumentId(response.document_id || '');
                    setVerificationUrl(response.verification_url || '');
                    setTotalSentences(typeof response.total_sentences === 'number' ? response.total_sentences : null);
                    setLastSigned(response.last_signed || '');
                    setSentenceSegments(Array.isArray(response.sentences) ? response.sentences : []);
                    setSentencesTotal(typeof response.sentences_total === 'number' ? response.sentences_total : 0);
                    if (response.usage && response.usage.api_calls) {
                        setUsage(response.usage.api_calls);
                    }
                    setShowAllSentences(false);
                })
                .catch(() => {
                    setStatus('error');
                });
        };

        useEffect(() => {
            fetchStatus();
        }, [postId]);

        const fetchManifest = () => {
            if (!postId || !isSigned) {
                return;
            }
            setVerifying(true);
            apiFetch({
                path: 'encypher-provenance/v1/verify',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': EncypherProvenanceConfig.nonce,
                },
                data: { post_id: postId }
            })
                .then((response) => {
                    setManifestData(response.metadata);
                    setShowManifest(true);
                    setVerifying(false);
                })
                .catch((error) => {
                    console.error('Failed to fetch manifest:', error);
                    setVerifying(false);
                });
        };

        const isSigned = status === 'c2pa_protected' || status === 'c2pa_verified' || status === 'signed' || status === 'verified';
        const isPublished = postStatus === 'publish';
        const isDraft = postStatus === 'draft' || postStatus === 'auto-draft';

        const verificationInfo = () => {
            if (isDraft && !isSigned) {
                return 'Draft - Will be auto-signed when published';
            }

            switch (status) {
                case 'c2pa_protected':
                case 'signed':
                    return 'Signed with C2PA - Auto-updates on publish';
                case 'c2pa_verified':
                case 'verified':
                    return 'Verified - Content authenticity confirmed';
                case 'tampered':
                    return 'Warning - Possible tampering detected';
                case 'modified':
                    return 'Modified - Will re-sign on next publish';
                case 'not_signed':
                    if (isPublished) {
                        return 'Published but not signed - Will sign on next update';
                    }
                    return 'Not yet signed - Will sign on publish';
                case 'loading':
                    return 'Loading status...';
                case 'error':
                    return 'Error loading status';
                default:
                    return 'Status unavailable';
            }
        };

        const renderMeta = () => {
            if (!isSigned) {
                return null;
            }

            const items = [];

            if (lastSigned) {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'last-signed', style: { fontSize: '12px', color: '#666' } },
                        wp.element.createElement('strong', null, 'Last signed:'),
                        ' ',
                        lastSigned
                    )
                );
            }

            if (typeof totalSentences === 'number') {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'sentences', style: { fontSize: '12px', color: '#666' } },
                        wp.element.createElement('strong', null, 'Sentences protected:'),
                        ' ',
                        totalSentences
                    )
                );
            }

            if (documentId) {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'document-id', style: { fontSize: '11px', color: '#999', fontFamily: 'monospace' } },
                        wp.element.createElement('strong', null, 'Document ID:'),
                        ' ',
                        documentId
                    )
                );
            }

            if (isSigned) {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'view-manifest', style: { marginTop: '12px' } },
                        wp.element.createElement(
                            Button,
                            {
                                variant: 'secondary',
                                onClick: fetchManifest,
                                disabled: verifying,
                                style: { width: '100%' }
                            },
                            verifying ? 'Loading...' : 'View C2PA Manifest'
                        )
                    )
                );
            }

            return wp.element.createElement('ul', { className: 'verification-meta', style: { listStyle: 'none', padding: 0, marginTop: '12px' } }, items);
        };

        const renderManifestViewer = () => {
            if (!showManifest || !manifestData) {
                return null;
            }

            return wp.element.createElement(
                'div',
                { style: { marginTop: '16px', padding: '12px', background: '#f8f9fa', borderRadius: '4px', border: '1px solid #ddd' } },
                wp.element.createElement(
                    'div',
                    { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' } },
                    wp.element.createElement('strong', { style: { fontSize: '13px' } }, 'C2PA Manifest'),
                    wp.element.createElement(
                        Button,
                        {
                            isSmall: true,
                            onClick: () => setShowManifest(false)
                        },
                        'Close'
                    )
                ),
                wp.element.createElement(
                    'pre',
                    {
                        style: {
                            background: '#2b2b2b',
                            color: '#f8f8f2',
                            padding: '12px',
                            borderRadius: '4px',
                            fontSize: '11px',
                            lineHeight: '1.4',
                            overflow: 'auto',
                            maxHeight: '400px',
                            margin: 0
                        }
                    },
                    JSON.stringify(manifestData, null, 2)
                )
            );
        };

        const renderSentenceVerification = () => {
            if (!isSigned) {
                return null;
            }

            if (!sentenceSegments.length) {
                return wp.element.createElement(
                    Notice,
                    { status: 'info', isDismissible: false, style: { marginTop: '12px' } },
                    'Sentence-level markers will appear after the next successful signing.'
                );
            }

            const visibleSegments = showAllSentences ? sentenceSegments : sentenceSegments.slice(0, 3);

            return wp.element.createElement(
                'div',
                { className: 'encypher-sentence-verification' },
                wp.element.createElement('h4', { className: 'encypher-section-title' }, 'Sentence verification'),
                wp.element.createElement(
                    'ul',
                    { className: 'encypher-sentence-list' },
                    visibleSegments.map((segment, index) =>
                        wp.element.createElement(
                            'li',
                            { key: `sentence-${segment.leaf_index}-${index}`, className: 'sentence-chip' },
                            wp.element.createElement(
                                'span',
                                { className: 'sentence-index' },
                                '#' + (typeof segment.leaf_index === 'number' ? segment.leaf_index : index + 1)
                            ),
                            wp.element.createElement(
                                'span',
                                { className: 'sentence-preview' },
                                segment.preview ? segment.preview : 'Text preview unavailable'
                            ),
                            segment.verification_url
                                ? wp.element.createElement(
                                      Button,
                                      {
                                          isSmall: true,
                                          onClick: () => window.open(segment.verification_url, '_blank', 'noopener,noreferrer'),
                                      },
                                      'Open verifier'
                                  )
                                : null
                        )
                    )
                ),
                sentencesTotal > 3
                    ? wp.element.createElement(
                          Button,
                          {
                              isSmall: true,
                              variant: 'link',
                              onClick: () => setShowAllSentences(!showAllSentences),
                          },
                          showAllSentences ? 'Show fewer sentences' : 'Show ' + (sentencesTotal - visibleSegments.length) + ' more'
                      )
                    : null
            );
        };

        return wp.element.createElement(
            PluginDocumentSettingPanel,
            {
                name: 'encypher-provenance-panel',
                title: 'Encypher Provenance',
                className: 'encypher-provenance-panel',
            },
            wp.element.createElement(
                'div',
                { className: 'encypher-provenance-status', style: { padding: '12px 0' } },
                renderBrandingPrimer(),
                renderUsageMeter(),
                status === 'loading' && wp.element.createElement(Spinner, null),
                status !== 'loading' && wp.element.createElement(
                    'div',
                    { style: { marginBottom: '12px', padding: '8px', backgroundColor: '#f0f0f1', borderRadius: '4px', fontSize: '13px', lineHeight: '1.5' } },
                    verificationInfo()
                ),
                renderMeta(),
                renderManifestViewer(),
                renderSentenceVerification(),
                !isSigned && isDraft && wp.element.createElement(
                    'p',
                    { style: { fontSize: '12px', color: '#666', fontStyle: 'italic', marginTop: '12px' } },
                    'Content will be automatically signed with C2PA when you publish this post.'
                )
            )
        );
    };

    const PrePublishPanel = function () {
        const postStatus = useSelect((select) => select('core/editor').getEditedPostAttribute('status'), []);
        const isDraft = postStatus === 'draft' || postStatus === 'auto-draft';
        const usage = (typeof EncypherProvenanceConfig !== 'undefined' && EncypherProvenanceConfig.usage && EncypherProvenanceConfig.usage.api_calls)
            ? EncypherProvenanceConfig.usage.api_calls
            : { used: 0, limit: 1000, remaining: 1000, percentage_used: 0, is_unlimited: false };
        const isUnlimited = Boolean(usage.is_unlimited) || Number(usage.limit) < 0;
        const summary = isUnlimited
            ? `Monthly API calls this month: ${Number(usage.used || 0).toLocaleString()} (Unlimited plan)`
            : `Monthly API calls this month: ${Number(usage.used || 0).toLocaleString()} / ${Number(usage.limit || 1000).toLocaleString()}`;

        return wp.element.createElement(
            PluginPrePublishPanel,
            {
                title: 'Encypher Content Signing (C2PA-compatible)',
                initialOpen: true,
            },
            wp.element.createElement(
                'div',
                { style: { padding: '12px 0' } },
                wp.element.createElement(
                    'p',
                    { style: { margin: '0 0 12px 0', fontSize: '13px', lineHeight: '1.5' } },
                    isDraft
                        ? 'This content will be automatically signed with C2PA when published.'
                        : 'This content will be re-signed with C2PA to reflect your changes.'
                ),
                wp.element.createElement(
                    'ul',
                    { style: { margin: '0', paddingLeft: '20px', fontSize: '12px', color: '#666' } },
                    wp.element.createElement('li', null, 'Cryptographic signature added'),
                    wp.element.createElement('li', null, 'Provenance metadata embedded'),
                    wp.element.createElement('li', null, 'Content authenticity verifiable')
                ),
                wp.element.createElement(
                    'p',
                    { style: { margin: '12px 0 0 0', fontSize: '11px', color: '#999', fontStyle: 'italic' } },
                    'Signing happens automatically - no action required.'
                ),
                wp.element.createElement(
                    'p',
                    { className: 'encypher-prepublish-usage' },
                    summary
                )
            )
        );
    };

    registerPlugin('encypher-provenance-sidebar', {
        render: function() {
            return wp.element.createElement(
                wp.element.Fragment,
                null,
                wp.element.createElement(StatusPanel),
                wp.element.createElement(PrePublishPanel)
            );
        },
        icon: 'shield',
    });
})();
