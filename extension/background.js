chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'verify-selection',
    title: 'Verify with EncypherAI',
    contexts: ['selection']
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'verify-selection' && tab?.id) {
    chrome.tabs.sendMessage(tab.id, { type: 'VERIFY_SELECTION', text: info.selectionText });
  }
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'STORE_RESULT') {
    chrome.storage.local.set({ lastResult: msg.data });
  }
});
