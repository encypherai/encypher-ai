(function (global) {
  function ensureAllowedApiUrl(urlString) {
    let parsed;
    try {
      parsed = new URL(urlString);
    } catch (err) {
      throw new Error('Invalid API base URL.');
    }

    if (parsed.protocol !== 'https:') {
      throw new Error('API base URL must use https.');
    }

    if (!(parsed.hostname === 'encypher.com' || parsed.hostname.endsWith('.encypher.com'))) {
      throw new Error('API base URL must be hosted on encypher.com.');
    }

    return parsed.origin;
  }

  async function request(url, options) {
    const response = await fetch(url, options);
    let body = {};
    try {
      body = await response.json();
    } catch (err) {
      throw new Error('API response was not valid JSON.');
    }

    if (!response.ok) {
      throw new Error((body.error && body.error.message) || body.detail || 'Email API request failed.');
    }

    return body;
  }

  async function signEmailBody(params) {
    const base = ensureAllowedApiUrl(params.apiBaseUrl);

    const payload = {
      text: params.text,
      document_title: params.title || 'Outlook Email',
      options: {
        document_type: 'email',
        return_embedding_plan: true,
      },
    };

    if (params.previousEmbeddings && params.previousEmbeddings.length > 0) {
      payload.options.previous_embeddings = params.previousEmbeddings;
    }

    const body = await request(base + '/api/v1/sign', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + params.apiKey,
      },
      body: JSON.stringify(payload),
    });

    const documentData = (body.data && body.data.document) || body.data || {};
    const signedText = documentData.signed_text || documentData.embedded_content;

    if (!signedText) {
      throw new Error('Sign response missing signed email body.');
    }

    return {
      signedText,
      embeddingPlan: documentData.embedding_plan || null,
      verificationUrl: documentData.verification_url || null,
      documentId: documentData.document_id || null,
      raw: body,
    };
  }

  async function verifyEmailBody(params) {
    const base = ensureAllowedApiUrl(params.apiBaseUrl);

    const body = await request(base + '/api/v1/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: params.text }),
    });

    return body.data || {};
  }

  global.EmailApi = {
    ensureAllowedApiUrl,
    signEmailBody,
    verifyEmailBody,
  };
})(typeof window !== 'undefined' ? window : globalThis);

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ensureAllowedApiUrl: globalThis.EmailApi.ensureAllowedApiUrl,
    signEmailBody: globalThis.EmailApi.signEmailBody,
  };
}
