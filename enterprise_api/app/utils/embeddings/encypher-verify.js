/**
 * Encypher Verification Library
 * 
 * JavaScript library for extracting and verifying Encypher embeddings from web pages.
 * Designed for browser extensions and client-side verification.
 * 
 * @version 1.0.0
 * @license MIT
 */

(function(global) {
    'use strict';

    const EncypherVerify = {
        /**
         * API endpoint for public verification
         */
        API_ENDPOINT: 'https://api.encypher.ai/api/v1/public/verify',

        /**
         * Extract all Encypher references from the current page
         * 
         * @returns {Array<Object>} Array of {element, embedding, ref_id, signature}
         */
        extractFromPage: function() {
            const references = [];

            // Method 1: Data attributes
            const dataElements = document.querySelectorAll('[data-encypher]');
            dataElements.forEach(el => {
                const embedding = el.getAttribute('data-encypher');
                const parsed = this.parseEmbedding(embedding);
                if (parsed) {
                    references.push({
                        element: el,
                        embedding: embedding,
                        ref_id: parsed.ref_id,
                        signature: parsed.signature,
                        method: 'data-attribute'
                    });
                }
            });

            // Method 2: Hidden spans
            const spanElements = document.querySelectorAll('span.ency-ref');
            spanElements.forEach(el => {
                const embedding = el.textContent;
                const parsed = this.parseEmbedding(embedding);
                if (parsed) {
                    references.push({
                        element: el.parentElement,
                        embedding: embedding,
                        ref_id: parsed.ref_id,
                        signature: parsed.signature,
                        method: 'span'
                    });
                }
            });

            // Method 3: HTML comments (requires parsing innerHTML)
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_COMMENT,
                null,
                false
            );

            let node;
            while (node = walker.nextNode()) {
                const comment = node.textContent;
                if (comment.includes('ency:')) {
                    const match = comment.match(/ency:v1\/([a-f0-9]{8})\/([a-zA-Z0-9]{8})/);
                    if (match) {
                        references.push({
                            element: node.parentElement,
                            embedding: `ency:v1/${match[1]}/${match[2]}`,
                            ref_id: match[1],
                            signature: match[2],
                            method: 'comment'
                        });
                    }
                }
            }

            console.log(`[EncypherVerify] Found ${references.length} embeddings`);
            return references;
        },

        /**
         * Parse an embedding string into components
         * 
         * @param {string} embedding - Embedding string (e.g., "ency:v1/a3f9c2e1/8k3mP9xQ")
         * @returns {Object|null} {version, ref_id, signature} or null if invalid
         */
        parseEmbedding: function(embedding) {
            if (!embedding || typeof embedding !== 'string') {
                return null;
            }

            const match = embedding.match(/^ency:(v\d+)\/([a-f0-9]{8})\/([a-zA-Z0-9]{8,})$/);
            if (!match) {
                return null;
            }

            return {
                version: match[1],
                ref_id: match[2],
                signature: match[3]
            };
        },

        /**
         * Verify a single embedding with the Encypher API
         * 
         * @param {string} ref_id - Reference ID (8 hex characters)
         * @param {string} signature - Signature (8+ hex characters)
         * @returns {Promise<Object>} Verification result
         */
        verify: async function(ref_id, signature) {
            try {
                const url = `${this.API_ENDPOINT}/${ref_id}?signature=${signature}`;
                const response = await fetch(url);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                return data;
            } catch (error) {
                console.error(`[EncypherVerify] Verification failed:`, error);
                return {
                    valid: false,
                    error: error.message
                };
            }
        },

        /**
         * Verify multiple embeddings in batch
         * 
         * @param {Array<Object>} references - Array of {ref_id, signature}
         * @returns {Promise<Object>} Batch verification result
         */
        verifyBatch: async function(references) {
            try {
                const url = `${this.API_ENDPOINT}/batch`;
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        references: references.map(r => ({
                            ref_id: r.ref_id,
                            signature: r.signature
                        }))
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                return data;
            } catch (error) {
                console.error(`[EncypherVerify] Batch verification failed:`, error);
                return {
                    results: [],
                    total: 0,
                    valid_count: 0,
                    invalid_count: 0,
                    error: error.message
                };
            }
        },

        /**
         * Verify all embeddings on the current page
         * 
         * @returns {Promise<Array<Object>>} Array of verification results
         */
        verifyPage: async function() {
            const references = this.extractFromPage();
            
            if (references.length === 0) {
                console.log('[EncypherVerify] No embeddings found on page');
                return [];
            }

            console.log(`[EncypherVerify] Verifying ${references.length} embeddings...`);

            // Use batch verification for efficiency
            const batchResult = await this.verifyBatch(references);

            // Merge results with original references
            const results = references.map((ref, index) => {
                const verificationResult = batchResult.results?.[index] || {
                    valid: false,
                    error: 'No result from server'
                };

                return {
                    ...ref,
                    verification: verificationResult
                };
            });

            const validCount = results.filter(r => r.verification.valid).length;
            console.log(`[EncypherVerify] Verified ${validCount}/${references.length} embeddings`);

            return results;
        },

        /**
         * Add visual indicators to verified content
         * 
         * @param {Array<Object>} results - Results from verifyPage()
         * @param {Object} options - Display options
         */
        displayVerificationBadges: function(results, options = {}) {
            const defaults = {
                showValid: true,
                showInvalid: true,
                badgePosition: 'top-right',
                badgeStyle: 'minimal'
            };
            const opts = { ...defaults, ...options };

            results.forEach(result => {
                if (!result.element) return;

                const isValid = result.verification.valid;

                if ((isValid && !opts.showValid) || (!isValid && !opts.showInvalid)) {
                    return;
                }

                // Create badge element
                const badge = document.createElement('span');
                badge.className = `encypher-badge encypher-badge-${isValid ? 'valid' : 'invalid'}`;
                badge.style.cssText = `
                    display: inline-block;
                    padding: 2px 6px;
                    margin-left: 4px;
                    font-size: 11px;
                    font-weight: bold;
                    border-radius: 3px;
                    cursor: help;
                    ${isValid 
                        ? 'background: #10b981; color: white;' 
                        : 'background: #ef4444; color: white;'}
                `;
                badge.textContent = isValid ? '✓ Verified' : '✗ Unverified';
                badge.title = isValid
                    ? `Verified by Encypher\nDocument: ${result.verification.document_id || 'Unknown'}`
                    : `Verification failed: ${result.verification.error || 'Unknown error'}`;

                // Add click handler for details
                badge.addEventListener('click', () => {
                    this.showVerificationDetails(result);
                });

                // Insert badge
                result.element.appendChild(badge);
            });
        },

        /**
         * Show detailed verification information in a modal
         * 
         * @param {Object} result - Verification result
         */
        showVerificationDetails: function(result) {
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                z-index: 10000;
                max-width: 500px;
                max-height: 80vh;
                overflow-y: auto;
            `;

            const verification = result.verification;
            
            modal.innerHTML = `
                <h3 style="margin-top: 0;">Encypher Verification</h3>
                <p><strong>Status:</strong> ${verification.valid ? '✓ Verified' : '✗ Unverified'}</p>
                ${verification.valid ? `
                    <p><strong>Document:</strong> ${verification.document?.title || verification.document?.document_id || 'Unknown'}</p>
                    <p><strong>Author:</strong> ${verification.document?.author || 'Unknown'}</p>
                    <p><strong>Organization:</strong> ${verification.document?.organization || 'Unknown'}</p>
                    <p><strong>License:</strong> ${verification.licensing?.license_type || 'Not specified'}</p>
                    <p><strong>Text Preview:</strong> ${verification.content?.text_preview || 'N/A'}</p>
                ` : `
                    <p><strong>Error:</strong> ${verification.error || 'Unknown error'}</p>
                `}
                <button id="encypher-close-modal" style="
                    margin-top: 10px;
                    padding: 8px 16px;
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                ">Close</button>
            `;

            // Add overlay
            const overlay = document.createElement('div');
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                z-index: 9999;
            `;

            document.body.appendChild(overlay);
            document.body.appendChild(modal);

            // Close handlers
            const closeModal = () => {
                document.body.removeChild(modal);
                document.body.removeChild(overlay);
            };

            modal.querySelector('#encypher-close-modal').addEventListener('click', closeModal);
            overlay.addEventListener('click', closeModal);
        }
    };

    // Export for different module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = EncypherVerify;
    } else if (typeof define === 'function' && define.amd) {
        define([], function() { return EncypherVerify; });
    } else {
        global.EncypherVerify = EncypherVerify;
    }

})(typeof window !== 'undefined' ? window : this);
