function getDocumentText_() {
  return DocumentApp.getActiveDocument().getBody().getText();
}

function getSelectionText_() {
  var doc = DocumentApp.getActiveDocument();
  var selection = doc.getSelection();
  if (!selection) {
    return '';
  }

  var pieces = [];
  var rangeElements = selection.getRangeElements();
  for (var i = 0; i < rangeElements.length; i += 1) {
    var rangeElement = rangeElements[i];
    var element = rangeElement.getElement();
    if (element.editAsText) {
      var textElement = element.editAsText();
      if (rangeElement.isPartial()) {
        pieces.push(textElement.getText().substring(rangeElement.getStartOffset(), rangeElement.getEndOffsetInclusive() + 1));
      } else {
        pieces.push(textElement.getText());
      }
    }
  }
  return pieces.join('\n');
}

function replaceSelectionText_(replacementText) {
  var doc = DocumentApp.getActiveDocument();
  var selection = doc.getSelection();
  if (!selection) {
    throw new Error('No text selected. Please select text and try again.');
  }

  var rangeElements = selection.getRangeElements();
  if (!rangeElements || rangeElements.length === 0) {
    throw new Error('No editable text found in selection.');
  }

  var insertionPoint = null;

  // Replace from end to start to avoid offset invalidation.
  for (var i = rangeElements.length - 1; i >= 0; i -= 1) {
    var rangeElement = rangeElements[i];
    var element = rangeElement.getElement();
    if (!element.editAsText) {
      continue;
    }

    var textElement = element.editAsText();
    var startOffset = rangeElement.isPartial() ? rangeElement.getStartOffset() : 0;
    var endOffset = rangeElement.isPartial()
      ? rangeElement.getEndOffsetInclusive()
      : Math.max(0, textElement.getText().length - 1);

    insertionPoint = {
      textElement: textElement,
      offset: startOffset,
    };

    if (endOffset >= startOffset) {
      textElement.deleteText(startOffset, endOffset);
    }
  }

  if (insertionPoint !== null) {
    insertionPoint.textElement.insertText(insertionPoint.offset, replacementText);
  }
}

function replaceDocumentText_(replacementText) {
  var body = DocumentApp.getActiveDocument().getBody();
  body.setText(replacementText);
}

function signCurrentSelection() {
  return runSignFlow_({ mode: 'selection' });
}

function signFullDocument() {
  return runSignFlow_({ mode: 'document' });
}

function verifyCurrentSelection() {
  return runVerifyFlow_({ mode: 'selection' });
}

function verifyFullDocument() {
  return runVerifyFlow_({ mode: 'document' });
}

function runSignFlow_(opts) {
  var mode = opts && opts.mode ? opts.mode : 'selection';
  var sourceText = mode === 'selection' ? getSelectionText_() : getDocumentText_();

  if (!sourceText || sourceText.trim().length < ENCYPHER_CONFIG.MIN_SIGN_TEXT_LENGTH) {
    throw new Error('Content too short to sign. Minimum ' + ENCYPHER_CONFIG.MIN_SIGN_TEXT_LENGTH + ' characters.');
  }

  var visibleText = stripEmbeddingChars_(sourceText);
  var visibleHash = hashText_(visibleText);

  var existingRuns = extractEmbeddingRuns_(sourceText);
  if (existingRuns.length > 0) {
    storeProvenanceRuns_(visibleHash, existingRuns, { source: mode + '-pre-sign' });
  }

  var previousEmbeddings = getProvenanceForHash_(visibleHash);
  var result = signWithEncypher_(sourceText, DocumentApp.getActiveDocument().getName(), previousEmbeddings);

  if (mode === 'selection') {
    replaceSelectionText_(result.signedText);
  } else {
    replaceDocumentText_(result.signedText);
  }

  return {
    mode: mode,
    success: true,
    documentId: result.documentId,
    verificationUrl: result.verificationUrl,
    signedLength: result.signedText.length,
    previousEmbeddingsCount: previousEmbeddings.length,
  };
}

function runVerifyFlow_(opts) {
  var mode = opts && opts.mode ? opts.mode : 'selection';
  var sourceText = mode === 'selection' ? getSelectionText_() : getDocumentText_();

  if (!sourceText || sourceText.trim().length === 0) {
    throw new Error('No content available to verify.');
  }

  var verdict = verifyWithEncypher_(sourceText);
  return {
    mode: mode,
    success: true,
    valid: verdict.valid === true,
    revoked: verdict.revoked === true,
    signerName: verdict.signer_name || verdict.organization_name || '',
    reasonCode: verdict.reason_code || '',
    timestamp: verdict.timestamp || '',
    raw: verdict,
  };
}
