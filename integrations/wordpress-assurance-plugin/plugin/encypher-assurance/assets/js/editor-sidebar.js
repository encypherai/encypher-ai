(function () {
    const { registerPlugin } = wp.plugins;
    const { PluginDocumentSettingPanel } = wp.editPost;
    const { Button, Notice, Spinner } = wp.components;
    const { useState, useEffect } = wp.element;
    const { useSelect } = wp.data;
    const apiFetch = wp.apiFetch;

    const StatusPanel = function () {
        const postId = useSelect((select) => select('core/editor').getCurrentPostId(), []);
        const [status, setStatus] = useState('loading');
        const [documentId, setDocumentId] = useState('');
        const [verificationUrl, setVerificationUrl] = useState('');
        const [totalSentences, setTotalSentences] = useState(null);
        const [message, setMessage] = useState('');
        const [isWorking, setIsWorking] = useState(false);

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
                    setMessage('');
                })
                .catch((error) => {
                    setStatus('error');
                    setMessage(error.message || 'Unable to fetch status.');
                });
        };

        useEffect(() => {
            fetchStatus();
        }, [postId]);

        const signContent = () => {
            if (!postId || isWorking) {
                return;
            }
            setIsWorking(true);
            setMessage('');

            apiFetch({
                path: 'encypher-assurance/v1/sign',
                method: 'POST',
                data: {
                    post_id: postId,
                },
                headers: {
                    'X-WP-Nonce': EncypherAssuranceConfig.nonce,
                },
            })
                .then((response) => {
                    if (response.signed_text) {
                        wp.data.dispatch('core/editor').editPost({ content: response.signed_text });
                        wp.data.dispatch('core/editor').savePost();
                    }
                    setStatus(response.status || 'signed');
                    setDocumentId(response.document_id || '');
                    setVerificationUrl(response.verification_url || '');
                    setTotalSentences(typeof response.total_sentences === 'number' ? response.total_sentences : null);
                    setMessage('Content signed successfully.');
                })
                .catch((error) => {
                    setMessage(error.message || 'Failed to sign content.');
                    setStatus('error');
                })
                .finally(() => {
                    setIsWorking(false);
                });
        };

        const verificationInfo = () => {
            switch (status) {
                case 'verified':
                    return 'Content authenticity verified.';
                case 'tampered':
                    return 'Verification detected possible tampering.';
                case 'signed':
                    return 'Content signed. Verification pending.';
                case 'modified':
                    return 'Content has been modified since the last signature.';
                case 'not_signed':
                    return 'Content has not been signed yet.';
                case 'loading':
                    return 'Loading current status...';
                case 'error':
                    return 'The plugin could not determine the current status.';
                default:
                    return 'Status unavailable.';
            }
        };

        const renderMeta = () => {
            if (!documentId && !verificationUrl && totalSentences === null) {
                return null;
            }

            const items = [];

            if (documentId) {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'document-id' },
                        wp.element.createElement('strong', null, 'Document ID:'),
                        ' ',
                        documentId
                    )
                );
            }

            if (verificationUrl) {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'verification-url' },
                        wp.element.createElement(
                            'a',
                            { href: verificationUrl, target: '_blank', rel: 'noopener' },
                            'View provenance report'
                        )
                    )
                );
            }

            if (typeof totalSentences === 'number') {
                items.push(
                    wp.element.createElement(
                        'li',
                        { key: 'sentences' },
                        wp.element.createElement('strong', null, 'Sentences protected:'),
                        ' ',
                        totalSentences
                    )
                );
            }

            return wp.element.createElement('ul', { className: 'verification-meta' }, items);
        };

        return wp.element.createElement(
            PluginDocumentSettingPanel,
            {
                name: 'encypher-assurance-panel',
                title: 'Encypher Assurance',
                className: 'encypher-assurance-panel',
            },
            wp.element.createElement(
                'div',
                { className: 'encypher-assurance-status' },
                status === 'loading' && wp.element.createElement(Spinner, null),
                status !== 'loading' && wp.element.createElement('p', { className: 'status-text' }, verificationInfo()),
                renderMeta(),
                message &&
                    wp.element.createElement(
                        Notice,
                        { status: status === 'error' ? 'error' : 'success', isDismissible: true },
                        message
                    ),
                wp.element.createElement(
                    Button,
                    {
                        isPrimary: true,
                        isBusy: isWorking,
                        onClick: signContent,
                    },
                    isWorking ? 'Signing...' : 'Sign Content'
                )
            )
        );
    };

    registerPlugin('encypher-assurance-sidebar', {
        render: StatusPanel,
        icon: 'shield',
    });
})();
