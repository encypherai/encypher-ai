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

        const fetchStatus = () => {
            if (!postId) {
                return;
            }
            setStatus('loading');
            apiFetch({
                path: `encypher-assurance/v1/status?post_id=${postId}`,
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
                })
                .catch((error) => {
                    setStatus('error');
                });
        };

        useEffect(() => {
            fetchStatus();
        }, [postId]);

        const isSigned = status === 'c2pa_protected' || status === 'c2pa_verified' || status === 'signed' || status === 'verified';
        const isPublished = postStatus === 'publish';
        const isDraft = postStatus === 'draft' || postStatus === 'auto-draft';

        const verificationInfo = () => {
            if (isDraft && !isSigned) {
                return '✏️ Draft - Will be auto-signed when published';
            }
            
            switch (status) {
                case 'c2pa_protected':
                case 'signed':
                    return '✓ Signed with C2PA - Auto-updates on publish';
                case 'c2pa_verified':
                case 'verified':
                    return '✓ Verified - Content authenticity confirmed';
                case 'tampered':
                    return '⚠️ Warning - Possible tampering detected';
                case 'modified':
                    return '📝 Modified - Will re-sign on next publish';
                case 'not_signed':
                    if (isPublished) {
                        return '⚠️ Published but not signed - Will sign on next update';
                    }
                    return '✏️ Not yet signed - Will sign on publish';
                case 'loading':
                    return 'Loading status...';
                case 'error':
                    return '❌ Error loading status';
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

            if (merkleRoot) {
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

            if (verificationUrl) {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'verification-url', style: { marginTop: '8px' } },
                        wp.element.createElement(
                            'a',
                            { href: verificationUrl, target: '_blank', rel: 'noopener', style: { textDecoration: 'none' } },
                            '🔍 View provenance report →'
                        )
                    )
                );
            }

            return wp.element.createElement('ul', { className: 'verification-meta', style: { listStyle: 'none', padding: 0, marginTop: '12px' } }, items);
        };

        return wp.element.createElement(
            PluginDocumentSettingPanel,
            {
                name: 'encypher-assurance-panel',
                title: 'Encypher C2PA',
                className: 'encypher-assurance-panel',
            },
            wp.element.createElement(
                'div',
                { className: 'encypher-assurance-status', style: { padding: '12px 0' } },
                status === 'loading' && wp.element.createElement(Spinner, null),
                status !== 'loading' && wp.element.createElement(
                    'div',
                    { style: { marginBottom: '12px', padding: '8px', backgroundColor: '#f0f0f1', borderRadius: '4px', fontSize: '13px', lineHeight: '1.5' } },
                    verificationInfo()
                ),
                renderMeta(),
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
                        ? '🔒 This content will be automatically signed with C2PA when published.'
                        : '🔒 This content will be re-signed with C2PA to reflect your changes.'
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

    registerPlugin('encypher-assurance-sidebar', {
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
