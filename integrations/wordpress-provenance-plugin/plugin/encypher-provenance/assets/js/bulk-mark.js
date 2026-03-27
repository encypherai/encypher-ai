/**
 * Bulk marking functionality for Encypher C2PA WordPress plugin.
 *
 * Handles batch processing of posts with progress tracking,
 * error handling, and pause/resume capabilities.
 */
(function($) {
    'use strict';

    const pricing = EncypherBulkMark.pricing || {};

    let bulkMarkState = {
        postIds: [],
        currentIndex: 0,
        batchSize: 10,
        successCount: 0,
        errorCount: 0,
        errors: [],
        isPaused: false,
        isCancelled: false,
        startTime: null,
        tier: EncypherBulkMark.tier || 'free'
    };

    /**
     * Initialize bulk marking interface.
     */
    function init() {
        // Update total count when selections change
        $('input[name="post_types[]"], input[name="status_filter"], select[name="date_range"]').on('change', updateTotalCount);

        // Show/hide custom date range
        $('#encypher-date-range').on('change', function() {
            if ($(this).val() === 'custom') {
                $('#encypher-custom-date-range').show();
            } else {
                $('#encypher-custom-date-range').hide();
            }
        });

        // Start bulk marking
        $('#encypher-start-bulk-mark').on('click', startBulkMarking);

        // Pause/resume
        $('#encypher-pause-bulk-mark').on('click', togglePause);

        // Cancel
        $('#encypher-cancel-bulk-mark').on('click', cancelBulkMarking);

        // Start new bulk operation
        $('#encypher-start-new-bulk').on('click', resetInterface);

        // View errors
        $('#encypher-view-errors').on('click', function(e) {
            e.preventDefault();
            $('.encypher-error-log').toggle();
        });

        // Payment setup button
        $('#encypher-setup-payment').on('click', openPaymentSetup);

        // Initial count update
        updateTotalCount();

        // Check payment status on load
        checkPaymentStatus();
    }

    /**
     * Update total count of posts to be marked.
     */
    function updateTotalCount() {
        const postTypes = $('input[name="post_types[]"]:checked').map(function() {
            return $(this).val();
        }).get();

        const statusFilter = $('input[name="status_filter"]:checked').val();
        const dateRange = $('#encypher-date-range').val();

        if (postTypes.length === 0) {
            $('#encypher-total-count').text('0');
            updateArchiveEstimate(0);
            return;
        }

        // Get count from server
        $.ajax({
            url: EncypherBulkMark.ajaxUrl,
            type: 'POST',
            data: {
                action: 'encypher_get_bulk_status',
                nonce: EncypherBulkMark.nonce,
                post_types: postTypes,
                status_filter: statusFilter,
                date_range: dateRange
            },
            success: function(response) {
                if (response.success) {
                    $('#encypher-total-count').text(response.data.total);
                    bulkMarkState.postIds = response.data.post_ids;
                    updateArchiveEstimate(response.data.total);
                }
            }
        });
    }

    function updateArchiveEstimate(totalCount) {
        const archivePricePerDocument = Number(pricing.archive_price_per_document || 0.01);
        const estimatedTotal = archivePricePerDocument * totalCount;
        $('#encypher-archive-estimate').text(formatCurrency(estimatedTotal));

        const $billingLink = $('#encypher-buy-archive-backfill');
        if ($billingLink.length) {
            const url = new URL(EncypherBulkMark.billingUrlBase || 'https://dashboard.encypher.com/billing');
            url.searchParams.set('addon', 'bulk-archive-backfill');
            url.searchParams.set('source', 'wordpress-plugin');
            if (totalCount > 0) {
                url.searchParams.set('quantity', String(totalCount));
            }
            $billingLink.attr('href', url.toString());
        }
    }

    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(amount);
    }

    /**
     * Start bulk marking process.
     */
    function startBulkMarking() {
        if (bulkMarkState.postIds.length === 0) {
            alert('No posts to mark. Please adjust your filters.');
            return;
        }

        // Reset state
        bulkMarkState.currentIndex = 0;
        bulkMarkState.successCount = 0;
        bulkMarkState.errorCount = 0;
        bulkMarkState.errors = [];
        bulkMarkState.isPaused = false;
        bulkMarkState.isCancelled = false;
        bulkMarkState.startTime = Date.now();
        bulkMarkState.batchSize = parseInt($('#encypher-batch-size').val()) || 10;

        // Show progress UI
        $('.encypher-bulk-form').hide();
        $('.encypher-bulk-progress').show();
        $('#encypher-progress-total').text(bulkMarkState.postIds.length);

        // Start processing
        processNextBatch();
    }

    /**
     * Process next batch of posts.
     */
    function processNextBatch() {
        if (bulkMarkState.isPaused) {
            $('#encypher-progress-status-text').text('Paused');
            return;
        }

        if (bulkMarkState.isCancelled) {
            $('#encypher-progress-status-text').text('Cancelled');
            showComplete();
            return;
        }

        if (bulkMarkState.currentIndex >= bulkMarkState.postIds.length) {
            // Complete
            showComplete();
            return;
        }

        // Get next batch
        const batchEnd = Math.min(
            bulkMarkState.currentIndex + bulkMarkState.batchSize,
            bulkMarkState.postIds.length
        );
        const batchIds = bulkMarkState.postIds.slice(bulkMarkState.currentIndex, batchEnd);

        $('#encypher-progress-status-text').text('Processing batch...');

        // Process batch - send post_ids as JSON string to avoid max_input_vars limit
        $.ajax({
            url: EncypherBulkMark.ajaxUrl,
            type: 'POST',
            data: {
                action: 'encypher_bulk_mark_batch',
                nonce: EncypherBulkMark.nonce,
                post_ids_json: JSON.stringify(batchIds)
            },
            success: function(response) {
                if (response.success) {
                    const results = response?.data?.results;
                    if (!Array.isArray(results)) {
                        handleBatchError('Invalid batch response from server.');
                        return;
                    }

                    if (results.length !== batchIds.length) {
                        handleBatchError(
                            'Incomplete batch response from server. Expected ' + batchIds.length + ' results but received ' + results.length + '.'
                        );
                        return;
                    }

                    processBatchResults(results);
                    bulkMarkState.currentIndex = batchEnd;
                    updateProgress();

                    // Continue to next batch
                    setTimeout(processNextBatch, 100);
                } else {
                    handleBatchError(response.data.message || 'Unknown error');
                }
            },
            error: function(xhr, status, error) {
                handleBatchError('AJAX error: ' + error);
            }
        });
    }

    /**
     * Process results from a batch.
     */
    function processBatchResults(results) {
        results.forEach(function(result) {
            if (result.success) {
                bulkMarkState.successCount++;
            } else {
                bulkMarkState.errorCount++;
                bulkMarkState.errors.push({
                    post_id: result.post_id,
                    post_title: result.post_title || 'Unknown',
                    error: result.error || 'Unknown error'
                });
            }

            // Update current post display
            $('#encypher-current-post-title').text(result.post_title || 'Unknown');
            $('#encypher-current-post-id').text(result.post_id);
        });
    }

    /**
     * Handle batch processing error.
     */
    function handleBatchError(message) {
        alert('Batch processing error: ' + message);
        bulkMarkState.isCancelled = true;
        showComplete();
    }

    /**
     * Update progress display.
     */
    function updateProgress() {
        const percentage = Math.round((bulkMarkState.currentIndex / bulkMarkState.postIds.length) * 100);

        $('.encypher-progress-fill').css('width', percentage + '%');
        $('#encypher-progress-percentage').text(percentage + '%');
        $('#encypher-progress-current').text(bulkMarkState.currentIndex);
        $('#encypher-success-count').text(bulkMarkState.successCount);
        $('#encypher-error-count').text(bulkMarkState.errorCount);

        if (bulkMarkState.errorCount > 0) {
            $('#encypher-view-errors').show();
            updateErrorLog();
        }

        // Update elapsed time
        const elapsed = Math.round((Date.now() - bulkMarkState.startTime) / 1000);
        $('#encypher-elapsed-time').text(elapsed + 's');
    }

    /**
     * Update error log display.
     */
    function updateErrorLog() {
        const $errorList = $('#encypher-error-list');
        $errorList.empty();

        bulkMarkState.errors.forEach(function(error) {
            $errorList.append(
                $('<li>').html(
                    '<strong>' + error.post_title + '</strong> (ID: ' + error.post_id + '): ' + error.error
                )
            );
        });
    }

    /**
     * Toggle pause state.
     */
    function togglePause() {
        bulkMarkState.isPaused = !bulkMarkState.isPaused;

        if (bulkMarkState.isPaused) {
            $('#encypher-pause-bulk-mark').text('Resume');
            $('#encypher-progress-status-text').text('Paused');
        } else {
            $('#encypher-pause-bulk-mark').text('Pause');
            $('#encypher-progress-status-text').text('Resuming...');
            processNextBatch();
        }
    }

    /**
     * Cancel bulk marking.
     */
    function cancelBulkMarking() {
        if (confirm('Are you sure you want to cancel? Progress will be lost.')) {
            bulkMarkState.isCancelled = true;
            $('#encypher-progress-status-text').text('Cancelling...');
        }
    }

    /**
     * Show completion screen.
     */
    function showComplete() {
        $('.encypher-bulk-progress').hide();
        $('.encypher-bulk-complete').show();

        $('#encypher-final-success-count').text(bulkMarkState.successCount);

        if (bulkMarkState.errorCount > 0) {
            $('#encypher-final-errors').show();
            $('#encypher-final-error-count').text(bulkMarkState.errorCount);
        }
    }

    /**
     * Reset interface for new bulk operation.
     */
    function resetInterface() {
        $('.encypher-bulk-complete').hide();
        $('.encypher-bulk-form').show();
        $('.encypher-error-log').hide();

        // Reset progress display
        $('.encypher-progress-fill').css('width', '0%');
        $('#encypher-progress-percentage').text('0%');
        $('#encypher-progress-current').text('0');
        $('#encypher-success-count').text('0');
        $('#encypher-error-count').text('0');
        $('#encypher-error-list').empty();
        $('#encypher-view-errors').hide();

        // Update count
        updateTotalCount();
    }

    /**
     * Check payment status from REST endpoint.
     */
    function checkPaymentStatus() {
        if (!EncypherBulkMark.paymentStatusUrl) {
            // No payment URL configured, hide the section
            $('#encypher-payment-status').hide();
            return;
        }

        $.ajax({
            url: EncypherBulkMark.paymentStatusUrl,
            type: 'GET',
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-WP-Nonce', EncypherBulkMark.restNonce);
            },
            success: function(response) {
                updatePaymentStatus(response);
            },
            error: function() {
                // On error, hide loading and don't block
                $('.encypher-payment-loading').hide();
            }
        });
    }

    /**
     * Update payment status UI based on response data.
     */
    function updatePaymentStatus(data) {
        $('.encypher-payment-loading').hide();

        if (data.has_payment_method) {
            $('.encypher-payment-active').show();
            $('.encypher-payment-missing').hide();
            if (data.default_card_last4) {
                $('#encypher-card-last4').text('(****' + data.default_card_last4 + ')');
            }
            // Enable buttons
            $('#encypher-start-bulk-mark').prop('disabled', false);
            $('#encypher-buy-archive-backfill').css('pointer-events', '');
        } else if (bulkMarkState.tier === 'free') {
            $('.encypher-payment-missing').show();
            $('.encypher-payment-active').hide();
            // Disable start and buy buttons for free tier without payment
            $('#encypher-start-bulk-mark').prop('disabled', true);
            $('#encypher-buy-archive-backfill').css('pointer-events', 'none');
        } else {
            // Enterprise/paid tiers without card -- don't block
            $('.encypher-payment-missing').hide();
            $('.encypher-payment-active').hide();
            $('#encypher-start-bulk-mark').prop('disabled', false);
        }
    }

    /**
     * Open payment setup in a popup and poll for completion.
     */
    function openPaymentSetup() {
        if (!EncypherBulkMark.paymentSetupUrl) {
            return;
        }

        var $btn = $('#encypher-setup-payment');
        $btn.prop('disabled', true).text('Opening...');

        $.ajax({
            url: EncypherBulkMark.paymentSetupUrl,
            type: 'POST',
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-WP-Nonce', EncypherBulkMark.restNonce);
            },
            success: function(response) {
                var checkoutUrl = response.checkout_url;
                if (!checkoutUrl) {
                    $btn.prop('disabled', false).text('Set Up Payment Method');
                    return;
                }

                var popup = window.open(checkoutUrl, 'encypher-payment', 'width=600,height=700');

                // Poll for popup close
                var pollTimer = setInterval(function() {
                    if (!popup || popup.closed) {
                        clearInterval(pollTimer);
                        $btn.prop('disabled', false).text('Set Up Payment Method');
                        // Re-check payment status after popup closes
                        $('.encypher-payment-loading').show();
                        $('.encypher-payment-missing').hide();
                        $('.encypher-payment-active').hide();
                        checkPaymentStatus();
                    }
                }, 1000);
            },
            error: function() {
                $btn.prop('disabled', false).text('Set Up Payment Method');
                alert('Failed to create payment setup session. Please try again.');
            }
        });
    }

    // Initialize on document ready
    $(document).ready(init);

})(jQuery);
