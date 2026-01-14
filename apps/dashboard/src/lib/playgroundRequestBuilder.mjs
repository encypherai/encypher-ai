/**
 * @typedef {{
 *   text?: string,
 *   document_title?: string,
 *   document_type?: string,
 *   template_id?: string,
 *   sentence_text?: string,
 * }} PlaygroundFormValues
 */

function normalizeString(value) {
  if (typeof value !== 'string') return undefined;
  const trimmed = value.trim();
  return trimmed ? trimmed : undefined;
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
    const text = normalizeString(values.text);
    if (!text) throw new Error('verify.text is required');
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
    const document_type = normalizeString(values.document_type);
    const template_id = normalizeString(values.template_id);

    return {
      ...(document_title ? { document_title } : {}),
      ...(document_type ? { document_type } : {}),
      text,
      ...(template_id ? { template_id } : {}),
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

  if (endpointId === 'verify') {
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
    return {
      text: typeof parsed.text === 'string' ? parsed.text : '',
      document_title: typeof parsed.document_title === 'string' ? parsed.document_title : '',
      document_type: typeof parsed.document_type === 'string' ? parsed.document_type : '',
      template_id: typeof parsed.template_id === 'string' ? parsed.template_id : '',
    };
  }

  return null;
}
