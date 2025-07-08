function highlightSelection(isValid) {
  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0) return;
  const range = sel.getRangeAt(0);
  const span = document.createElement('span');
  span.style.backgroundColor = isValid ? 'rgba(0,255,0,0.3)' : 'rgba(255,0,0,0.3)';
  range.surroundContents(span);
  sel.removeAllRanges();
}

function showOverlay(data) {
  const existing = document.getElementById('encypher-overlay');
  if (existing) existing.remove();
  const div = document.createElement('div');
  div.id = 'encypher-overlay';
  div.style.position = 'fixed';
  div.style.top = '10px';
  div.style.right = '10px';
  div.style.zIndex = '9999';
  div.style.backgroundColor = 'white';
  div.style.border = '1px solid #ccc';
  div.style.padding = '8px';
  div.style.fontSize = '14px';
  div.style.maxWidth = '250px';
  div.style.display = 'flex';
  div.style.alignItems = 'center';

  const img = document.createElement('img');
  img.src = chrome.runtime.getURL('icon.png');
  img.style.width = '16px';
  img.style.height = '16px';
  img.style.marginRight = '6px';

  const span = document.createElement('span');
  span.textContent = `Result: ${data.is_valid ? 'Valid' : 'Invalid'} - Model: ${data.payload?.ai_info?.model_id || 'Unknown'}`;

  div.appendChild(img);
  div.appendChild(span);
  document.body.appendChild(div);
  setTimeout(() => div.remove(), 5000);
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'VERIFY_SELECTION') {
    fetch('http://localhost:8000/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: msg.text })
    }).then(r => r.json()).then(data => {
      highlightSelection(data.is_valid);
      showOverlay(data);
      chrome.runtime.sendMessage({ type: 'STORE_RESULT', data });
    }).catch(err => console.error('Verification failed', err));
  }
});
