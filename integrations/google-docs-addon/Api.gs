function signWithEncypher_(text, title, previousEmbeddings) {
  var apiKey = requireApiKey_();
  var url = getApiBaseUrl_() + ENCYPHER_CONFIG.SIGN_PATH;

  var payload = {
    text: text,
    document_title: title || undefined,
    options: {
      document_type: 'article',
      return_embedding_plan: true,
    },
  };

  if (previousEmbeddings && previousEmbeddings.length > 0) {
    payload.options.previous_embeddings = previousEmbeddings;
  }

  var response = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + apiKey,
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });

  var status = response.getResponseCode();
  var body = response.getContentText() || '{}';
  var data;
  try {
    data = JSON.parse(body);
  } catch (err) {
    throw new Error('Invalid sign response from API (HTTP ' + status + ').');
  }

  if (status < 200 || status >= 300) {
    var errorMessage = (data.error && data.error.message) || data.detail || ('Signing failed (HTTP ' + status + ')');
    throw new Error(errorMessage);
  }

  var documentData = (data.data && data.data.document) || data.data || {};
  var signedText = documentData.signed_text || documentData.embedded_content;
  if (!signedText) {
    throw new Error('Sign response missing signed content.');
  }

  return {
    signedText: signedText,
    embeddingPlan: documentData.embedding_plan || null,
    documentId: documentData.document_id || null,
    verificationUrl: documentData.verification_url || null,
    tier: (data.meta && data.meta.tier) || null,
  };
}

function verifyWithEncypher_(text) {
  var url = getApiBaseUrl_() + ENCYPHER_CONFIG.VERIFY_PATH;

  var response = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ text: text }),
    muteHttpExceptions: true,
  });

  var status = response.getResponseCode();
  var body = response.getContentText() || '{}';
  var data;
  try {
    data = JSON.parse(body);
  } catch (err) {
    throw new Error('Invalid verify response from API (HTTP ' + status + ').');
  }

  if (status < 200 || status >= 300) {
    var errorMessage = (data.error && data.error.message) || data.detail || ('Verification failed (HTTP ' + status + ')');
    throw new Error(errorMessage);
  }

  return data.data || {};
}
