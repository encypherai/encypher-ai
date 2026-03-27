function getAddonState() {
  var apiKey = getApiKey_();
  var apiBaseUrl = getApiBaseUrl_();
  var docName = DocumentApp.getActiveDocument().getName();
  var selectionText = getSelectionText_();

  return {
    hasApiKey: !!apiKey,
    apiBaseUrl: apiBaseUrl,
    docName: docName,
    selectionChars: selectionText ? selectionText.length : 0,
    minChars: ENCYPHER_CONFIG.MIN_SIGN_TEXT_LENGTH,
  };
}

function saveAddonSettings(input) {
  var apiKey = (input && input.apiKey ? input.apiKey : '').trim();
  var apiBaseUrl = (input && input.apiBaseUrl ? input.apiBaseUrl : '').trim();

  if (apiBaseUrl && !isAllowedApiBaseUrl_(apiBaseUrl)) {
    throw new Error('API base URL must be https and hosted on encypher.com.');
  }

  var userProps = getUserProperties_();
  if (apiKey) {
    userProps.setProperty(ENCYPHER_CONFIG.PROPERTY_API_KEY, apiKey);
  }
  if (apiBaseUrl) {
    userProps.setProperty(ENCYPHER_CONFIG.PROPERTY_API_BASE_URL, apiBaseUrl);
  }

  return {
    success: true,
    hasApiKey: !!getApiKey_(),
    apiBaseUrl: getApiBaseUrl_(),
  };
}

function clearAddonSettings() {
  var userProps = getUserProperties_();
  userProps.deleteProperty(ENCYPHER_CONFIG.PROPERTY_API_KEY);
  userProps.deleteProperty(ENCYPHER_CONFIG.PROPERTY_API_BASE_URL);
  return { success: true };
}

function sidebarSignSelection() {
  return runSignFlow_({ mode: 'selection' });
}

function sidebarSignDocument() {
  return runSignFlow_({ mode: 'document' });
}

function sidebarVerifySelection() {
  return runVerifyFlow_({ mode: 'selection' });
}

function sidebarVerifyDocument() {
  return runVerifyFlow_({ mode: 'document' });
}

function sidebarGetProvenanceSummary() {
  var text = getSelectionText_() || getDocumentText_();
  var visibleHash = hashText_(stripEmbeddingChars_(text));
  var entries = getProvenanceForHash_(visibleHash);

  return {
    visibleHash: visibleHash,
    count: entries.length,
    entries: entries,
  };
}
