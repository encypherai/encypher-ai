/**
 * Helpers for embedding-plan aware signing flows.
 */

/**
 * Ensure sign requests always ask for embedding plan output.
 */
export function withEmbeddingPlanRequest(options = {}) {
  return {
    ...options,
    return_embedding_plan: true,
  };
}

/**
 * Rebuild signed text by inserting invisible marker chars at codepoint indexes.
 * Returns null when the plan is malformed for the provided visible text.
 */
export function applyEmbeddingPlanToText(visibleText, embeddingPlan) {
  const source = typeof visibleText === 'string' ? visibleText : '';

  if (!embeddingPlan || !Array.isArray(embeddingPlan.operations)) {
    return null;
  }

  const chars = [...source];
  const byIndex = new Map();

  for (const op of embeddingPlan.operations) {
    if (!op || typeof op.marker !== 'string' || typeof op.insert_after_index !== 'number') {
      return null;
    }
    const idx = op.insert_after_index;
    if (!Number.isInteger(idx) || idx < -1 || idx >= chars.length) {
      return null;
    }
    byIndex.set(idx, `${byIndex.get(idx) || ''}${op.marker}`);
  }

  let output = byIndex.get(-1) || '';
  for (let i = 0; i < chars.length; i += 1) {
    output += chars[i];
    if (byIndex.has(i)) {
      output += byIndex.get(i);
    }
  }
  return output;
}

/**
 * Prefer direct signed_text, then embedded_content, then plan reconstruction.
 */
export function resolveSignedText({ visibleText, result }) {
  if (!result || typeof result !== 'object') {
    return null;
  }

  if (typeof result.signed_text === 'string' && result.signed_text.length > 0) {
    return result.signed_text;
  }

  if (typeof result.embedded_content === 'string' && result.embedded_content.length > 0) {
    return result.embedded_content;
  }

  return applyEmbeddingPlanToText(visibleText, result.embedding_plan);
}
