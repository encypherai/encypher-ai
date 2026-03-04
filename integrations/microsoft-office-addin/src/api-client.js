(function (global) {
  function ensureHttpsEncypherHost(urlString) {
    let parsed;
    try {
      parsed = new URL(urlString);
    } catch (err) {
      throw new Error('Invalid API base URL.');
    }

    if (parsed.protocol !== 'https:') {
      throw new Error('API base URL must use https.');
    }

    if (!(parsed.hostname === 'encypherai.com' || parsed.hostname.endsWith('.encypherai.com'))) {
      throw new Error('API base URL must be hosted on encypherai.com.');
    }

    return parsed.origin;
  }

  async function request(url, options) {
    const response = await fetch(url, options);
    let data = {};

    try {
      data = await response.json();
    } catch (err) {
      throw new Error('Received non-JSON response from API.');
    }

    if (!response.ok) {
      throw new Error((data.error && data.error.message) || data.detail || 'API request failed.');
    }

    return data;
  }

  async function signContent(params) {
    const { apiBaseUrl, apiKey, text, title, previousEmbeddings } = params;
    const base = ensureHttpsEncypherHost(apiBaseUrl);

    const payload = {
      text,
      document_title: title || undefined,
      options: {
        segmentation_level: 'sentence',
        manifest_mode: 'micro',
        document_type: 'article',
        return_embedding_plan: true,
      },
    };

    if (previousEmbeddings && previousEmbeddings.length > 0) {
      payload.options.previous_embeddings = previousEmbeddings;
    }

    const body = await request(base + '/api/v1/sign', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + apiKey,
      },
      body: JSON.stringify(payload),
    });

    const documentData = (body.data && body.data.document) || body.data || {};
    const signedText = documentData.signed_text || documentData.embedded_content;

    if (!signedText) {
      throw new Error('Sign response missing signed content.');
    }

    return {
      signedText,
      embeddingPlan: documentData.embedding_plan || null,
      documentId: documentData.document_id || null,
      verificationUrl: documentData.verification_url || null,
      raw: body,
    };
  }

  async function verifyContent(params) {
    const { apiBaseUrl, text } = params;
    const base = ensureHttpsEncypherHost(apiBaseUrl);

    const body = await request(base + '/api/v1/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    return body.data || {};
  }

  global.EncypherApi = {
    ensureHttpsEncypherHost,
    signContent,
    verifyContent,
  };
})(typeof window !== 'undefined' ? window : globalThis);

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ensureHttpsEncypherHost: globalThis.EncypherApi.ensureHttpsEncypherHost,
    signContent: globalThis.EncypherApi.signContent,
    verifyContent: globalThis.EncypherApi.verifyContent,
  };
}
