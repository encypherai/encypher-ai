document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.local.get('lastResult', ({ lastResult }) => {
    if (!lastResult) return;
    const div = document.getElementById('result');
    div.textContent = `Last result: ${lastResult.is_valid ? 'Valid' : 'Invalid'} - Model: ${lastResult.payload?.ai_info?.model_id || 'Unknown'}`;
  });
});
