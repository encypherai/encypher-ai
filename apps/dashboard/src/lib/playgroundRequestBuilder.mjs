/**
 * @typedef {{
 *   text?: string,
 *   document_title?: string,
 *   document_type?: string,
 *   template_id?: string,
 *   sentence_text?: string,
 *   segmentation_level?: string,
 *   manifest_mode?: string,
 *   embedding_strategy?: string,
 * }} PlaygroundFormValues
 */

function normalizeString(value) {
  if (typeof value !== 'string') return undefined;
  const trimmed = value.trim();
  return trimmed ? trimmed : undefined;
}

/**
 * For verify endpoint: preserve exact text including invisible metadata.
 * C2PA signed content includes invisible Unicode variation selectors and wrappers
 * that MUST NOT be trimmed or normalized.
 */
function preserveExactString(value) {
  if (typeof value !== 'string') return undefined;
  if (value.length === 0) return undefined;
  if (value.trim().length === 0) return undefined;
  return value;
}

/**
 * @param {string} endpointId
 * @param {PlaygroundFormValues} values
 */
export function buildRequestObject(endpointId, values) {
  if (!values || typeof values !== 'object') {
    throw new Error('values must be an object');
  }

  if (endpointId === 'verify') {
    const text = preserveExactString(values.text);
    if (!text) throw new Error('verify.text is required');
    return { text };
  }

  if (endpointId === 'verify-advanced') {
    const text = preserveExactString(values.text);
    if (!text) throw new Error('verify-advanced.text is required');
    return { text };
  }

  if (endpointId === 'lookup') {
    const sentence_text = normalizeString(values.sentence_text);
    if (!sentence_text) throw new Error('lookup.sentence_text is required');
    return { sentence_text };
  }

  if (endpointId === 'sign') {
    const text = normalizeString(values.text);
    if (!text) throw new Error('sign.text is required');

    const document_title = normalizeString(values.document_title);
    const template_id = normalizeString(values.template_id);

    // Build options object for advanced fields.
    const options = {};
    const document_type = normalizeString(values.document_type);
    const segmentation_level = normalizeString(values.segmentation_level);
    if (segmentation_level) options.segmentation_level = segmentation_level;
    const manifest_mode = normalizeString(values.manifest_mode);
    if (manifest_mode) options.manifest_mode = manifest_mode;
    const embedding_strategy = normalizeString(values.embedding_strategy);
    if (embedding_strategy) options.embedding_strategy = embedding_strategy;

    return {
      text,
      ...(document_title ? { document_title } : {}),
      ...(document_type ? { document_type } : {}),
      ...(template_id ? { template_id } : {}),
      ...(Object.keys(options).length > 0 ? { options } : {}),
    };
  }

  throw new Error(`Unsupported endpointId: ${endpointId}`);
}

/**
 * @param {string} endpointId
 * @param {PlaygroundFormValues} values
 */
export function buildRequestBodyJson(endpointId, values) {
  const obj = buildRequestObject(endpointId, values);
  return JSON.stringify(obj, null, 2);
}

/**
 * Best-effort parse from JSON request body into form values.
 * @param {string} endpointId
 * @param {string} json
 */
export function parseRequestBodyJson(endpointId, json) {
  if (typeof json !== 'string') return null;
  let parsed;
  try {
    parsed = JSON.parse(json);
  } catch {
    return null;
  }

  if (!parsed || typeof parsed !== 'object') return null;

  if (endpointId === 'verify' || endpointId === 'verify-advanced') {
    return {
      text: typeof parsed.text === 'string' ? parsed.text : '',
    };
  }

  if (endpointId === 'lookup') {
    return {
      sentence_text: typeof parsed.sentence_text === 'string' ? parsed.sentence_text : '',
    };
  }

  if (endpointId === 'sign') {
    const opts = (parsed.options && typeof parsed.options === 'object') ? parsed.options : {};
    const segmentation_level = typeof opts.segmentation_level === 'string' ? opts.segmentation_level : '';
    const manifest_mode = typeof opts.manifest_mode === 'string' ? opts.manifest_mode : '';
    const embedding_strategy = typeof opts.embedding_strategy === 'string' ? opts.embedding_strategy : '';

    return {
      text: typeof parsed.text === 'string' ? parsed.text : '',
      document_title: typeof parsed.document_title === 'string' ? parsed.document_title : '',
      document_type: typeof opts.document_type === 'string' ? opts.document_type : (typeof parsed.document_type === 'string' ? parsed.document_type : ''),
      template_id: typeof parsed.template_id === 'string' ? parsed.template_id : '',
      ...(segmentation_level ? { segmentation_level } : {}),
      ...(manifest_mode ? { manifest_mode } : {}),
      ...(embedding_strategy ? { embedding_strategy } : {}),
    };
  }

  return null;
}
