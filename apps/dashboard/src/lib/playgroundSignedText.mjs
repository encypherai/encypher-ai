export function extractSignedTextFromResponse(responseText) {
  if (!responseText) return null;

  try {
    const data = JSON.parse(responseText);

    const unifiedSignedText = data?.success ? data?.data?.document?.signed_text : null;
    if (typeof unifiedSignedText === 'string' && unifiedSignedText.length > 0) {
      return unifiedSignedText;
    }

    const legacySignedText = data?.success ? data?.signed_text : null;
    if (typeof legacySignedText === 'string' && legacySignedText.length > 0) {
      return legacySignedText;
    }

    return null;
  } catch {
    return null;
  }
}
