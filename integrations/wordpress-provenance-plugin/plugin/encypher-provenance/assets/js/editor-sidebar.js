(function () {
    const { registerPlugin } = wp.plugins;
    const { PluginDocumentSettingPanel, PluginPrePublishPanel } = wp.editPost;
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
        const [merkleRoot, setMerkleRoot] = useState('');
        const [showManifest, setShowManifest] = useState(false);
        const [manifestData, setManifestData] = useState(null);
        const [verifying, setVerifying] = useState(false);
        const [sentenceSegments, setSentenceSegments] = useState([]);
        const [sentencesTotal, setSentencesTotal] = useState(0);
        const [merkleSummary, setMerkleSummary] = useState(null);
        const [showAllSentences, setShowAllSentences] = useState(false);
        const [copyingRoot, setCopyingRoot] = useState(false);
        const tier = (typeof EncypherAssuranceConfig !== 'undefined' && EncypherAssuranceConfig.tier) ? EncypherAssuranceConfig.tier : 'free';
        const upgradeUrl = (typeof EncypherAssuranceConfig !== 'undefined' && EncypherAssuranceConfig.upgradeUrl) ? EncypherAssuranceConfig.upgradeUrl : 'https://dashboard.encypherai.com/billing';

        const renderUpgradeCallout = (message) => {
            return wp.element.createElement(
                'div',
                { className: 'encypher-upgrade-callout' },
                wp.element.createElement('p', null, message),
                upgradeUrl
                    ? wp.element.createElement(
                          'a',
                          { href: upgradeUrl, className: 'button button-primary', target: '_blank', rel: 'noopener noreferrer' },
                          'Upgrade to Enterprise'
                      )
                    : null
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
                    'X-WP-Nonce': EncypherAssuranceConfig.nonce,
                },
            })
                .then((response) => {
                    setStatus(response.status || 'not_signed');
                    setDocumentId(response.document_id || '');
                    setVerificationUrl(response.verification_url || '');
                    setTotalSentences(typeof response.total_sentences === 'number' ? response.total_sentences : null);
                    setLastSigned(response.last_signed || '');
                    setMerkleRoot(response.merkle_root_hash || '');
                    setSentenceSegments(Array.isArray(response.sentences) ? response.sentences : []);
                    setSentencesTotal(typeof response.sentences_total === 'number' ? response.sentences_total : 0);
                    setMerkleSummary(response.merkle || null);
                    setShowAllSentences(false);
                })
                .catch((error) => {
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
            if (tier === 'free') {
                if (upgradeUrl) {
                    window.open(upgradeUrl, '_blank', 'noopener,noreferrer');
                }
                return;
            }
            setVerifying(true);
            apiFetch({
                path: 'encypher-provenance/v1/verify',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': EncypherAssuranceConfig.nonce,
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
            const canViewManifest = tier !== 'free';
            const pushUpgradeItem = (message, key) => {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key, style: { marginTop: '12px' } },
                        renderUpgradeCallout(message)
                    )
                );
            };

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

            if (typeof totalSentences === 'number' && canViewManifest) {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'sentences', style: { fontSize: '12px', color: '#666' } },
                        wp.element.createElement('strong', null, 'Sentences protected:'),
                        ' ',
                        totalSentences
                    )
                );
            } else if (tier === 'free') {
                pushUpgradeItem('Unlock sentence-level analytics with Encypher Enterprise.', 'upgrade-sentences');
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

            if (merkleRoot && canViewManifest) {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'merkle-root', style: { fontSize: '11px', color: '#999', fontFamily: 'monospace' } },
                        wp.element.createElement('strong', null, 'Merkle Root:'),
                        ' ',
                        merkleRoot.substring(0, 16) + '...'
                    )
                );
            }

            if (isSigned && canViewManifest) {
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
            } else if (isSigned && !canViewManifest) {
                pushUpgradeItem('Upgrade to view the underlying C2PA manifest.', 'upgrade-manifest');
            }

            return wp.element.createElement('ul', { className: 'verification-meta', style: { listStyle: 'none', padding: 0, marginTop: '12px' } }, items);
        };

        const renderManifestViewer = () => {
            if (!showManifest || !manifestData || tier === 'free') {
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
                ),
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
    } else if (isSigned && !canViewManifest) {
        pushUpgradeItem('Upgrade to view the underlying C2PA manifest.', 'upgrade-manifest');
    }

    return wp.element.createElement('ul', { className: 'verification-meta', style: { listStyle: 'none', padding: 0, marginTop: '12px' } }, items);
};
            if (!isSigned) {
                return null;
            }

            if (tier === 'free') {
                return renderUpgradeCallout('Unlock sentence-level verification with Encypher Enterprise.');
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
                                `#${typeof segment.leaf_index === 'number' ? segment.leaf_index : index + 1}`
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
                          showAllSentences ? 'Show fewer sentences' : `Show ${sentencesTotal - visibleSegments.length} more`
                      )
                    : null
            );
        };

        const renderMerkleSummary = () => {
            if (!isSigned) {
                return null;
            }

            if (!merkleSummary || !merkleSummary.root_hash) {
                if (tier === 'free') {
                    return null;
                }
                return wp.element.createElement(
                    Notice,
                    { status: 'info', isDismissible: false, style: { marginTop: '12px' } },
                    'Merkle proofs will be generated the next time this post is signed.'
                );
            }

            const rows = [
                { label: 'Root hash', value: merkleSummary.root_hash ? `${merkleSummary.root_hash.substring(0, 24)}…` : '—' },
                { label: 'Leaves', value: typeof merkleSummary.total_leaves === 'number' ? merkleSummary.total_leaves : 0 },
                {
                    label: 'Tree depth',
                    value: typeof merkleSummary.tree_depth === 'number' ? merkleSummary.tree_depth : '—',
                },
            ];

            const handleCopy = () => {
                if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard
                        .writeText(merkleSummary.root_hash)
                        .then(() => {
                            setCopyingRoot(true);
                            setTimeout(() => setCopyingRoot(false), 1500);
                        })
                        .catch(() => setCopyingRoot(false));
                } else {
                    window.prompt('Copy Merkle root', merkleSummary.root_hash);
                }
            };

            return wp.element.createElement(
                'div',
                { className: 'encypher-merkle-card' },
                wp.element.createElement('h4', { className: 'encypher-section-title' }, 'Merkle snapshot'),
                wp.element.createElement(
                    'ul',
                    { className: 'encypher-merkle-list' },
                    rows.map((row) =>
                        wp.element.createElement(
                            'li',
                            { key: row.label },
                            wp.element.createElement('span', { className: 'label' }, row.label),
                            wp.element.createElement('span', { className: 'value' }, row.value)
                        )
                    )
                ),
                wp.element.createElement(
                    Button,
                    {
                        isSecondary: true,
                        isSmall: true,
                        disabled: copyingRoot,
                        onClick: handleCopy,
                    },
                    copyingRoot ? 'Copied!' : 'Copy root hash'
                )
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
                status === 'loading' && wp.element.createElement(Spinner, null),
                status !== 'loading' && wp.element.createElement(
                    'div',
                    { style: { marginBottom: '12px', padding: '8px', backgroundColor: '#f0f0f1', borderRadius: '4px', fontSize: '13px', lineHeight: '1.5' } },
                    verificationInfo()
                ),
                renderMeta(),
                renderManifestViewer(),
                renderSentenceVerification(),
                renderMerkleSummary(),
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
        const isPublished = postStatus === 'publish';

        return wp.element.createElement(
            PluginPrePublishPanel,
            {
                title: 'C2PA Content Signing',
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
