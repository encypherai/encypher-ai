(function ($) {
    function normalizeStatus(status) {
        switch (status) {
            case 'verified':
                return 'Verified';
            case 'tampered':
                return 'Tampered';
            case 'signed':
                return 'Signed';
            case 'modified':
                return 'Modified';
            case 'loading':
                return 'Loading';
            case 'error':
                return 'Error';
            default:
                return 'Not signed';
        }
    }

    function updateStatus($container, status, message, extras) {
        var $statusValue = $container.find('.status-value');
        var $statusMessage = $container.find('.status-message');
        var $documentIdValue = $container.find('.document-id-value');
        var $verificationLink = $container.find('.verification-link');
        var $verificationAnchor = $verificationLink.find('a');
        var $sentencesCount = $container.find('.sentences-count');
        var $sentencesValue = $container.find('.sentences-value');

        $statusValue.text(normalizeStatus(status));

        if (message) {
            $statusMessage
                .text(message)
                .removeClass('error success')
                .addClass(status === 'error' ? 'error' : 'success');
        } else {
            $statusMessage.text('').removeClass('error success');
        }

        if (extras && extras.documentId) {
            $documentIdValue.text(extras.documentId);
        } else {
            $documentIdValue.text('Not available');
        }

        if (extras && extras.verificationUrl) {
            $verificationAnchor.attr('href', extras.verificationUrl);
            $verificationLink.show();
        } else {
            $verificationAnchor.attr('href', '#');
            $verificationLink.hide();
        }

        if (extras && typeof extras.totalSentences === 'number') {
            $sentencesValue.text(extras.totalSentences);
            $sentencesCount.toggle(extras.totalSentences > 0);
        } else {
            $sentencesValue.text('0');
            $sentencesCount.hide();
        }
    }

    $(document).on('click', '.encypher-provenance-sign', function () {
        var $button = $(this);
        var $container = $button.closest('.encypher-provenance-classic');
        var postId = $button.data('post-id');

        if (!postId) {
            return;
        }

        $button.prop('disabled', true).text('Signing...');
        updateStatus($container, 'loading', 'Signing content...', {});

        $.ajax({
            url: EncypherAssuranceClassic.restUrl + 'sign',
            method: 'POST',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-WP-Nonce', EncypherAssuranceClassic.nonce);
            },
            data: {
                post_id: postId,
            },
        })
            .done(function (response) {
                updateStatus($container, response.status || 'signed', 'Content signed successfully.', {
                    documentId: response.document_id || '',
                    verificationUrl: response.verification_url || '',
                    totalSentences:
                        typeof response.total_sentences === 'number' ? response.total_sentences : 0,
                });

                if (response.signed_text) {
                    window.location.reload();
                }
            })
            .fail(function (jqXHR) {
                var message = 'Failed to sign content.';
                if (jqXHR.responseJSON && jqXHR.responseJSON.message) {
                    message = jqXHR.responseJSON.message;
                }
                updateStatus($container, 'error', message, {});
            })
            .always(function () {
                $button.prop('disabled', false).text('Sign Content');
            });
    });
})(jQuery);
