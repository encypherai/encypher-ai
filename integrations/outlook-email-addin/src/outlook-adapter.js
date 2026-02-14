(function (global) {
  function getMailboxItem() {
    if (!global.Office || !Office.context || !Office.context.mailbox || !Office.context.mailbox.item) {
      throw new Error('Outlook mailbox item unavailable.');
    }
    return Office.context.mailbox.item;
  }

  function getModeLabel() {
    const item = getMailboxItem();
    const itemType = item.itemType || 'UnknownItem';
    const mode = item.displayReplyForm ? 'compose_or_read' : 'read';
    return itemType + ' (' + mode + ')';
  }

  function getSubject() {
    const item = getMailboxItem();
    return item.subject || 'Outlook Email';
  }

  function getBody(options) {
    const item = getMailboxItem();
    const coercionType = (options && options.html)
      ? Office.CoercionType.Html
      : Office.CoercionType.Text;

    return new Promise((resolve, reject) => {
      item.body.getAsync(coercionType, (result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          resolve((result.value || '').toString());
        } else {
          reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to read Outlook body.'));
        }
      });
    });
  }

  function setBody(content, options) {
    const item = getMailboxItem();
    const coercionType = (options && options.html)
      ? Office.CoercionType.Html
      : Office.CoercionType.Text;

    return new Promise((resolve, reject) => {
      item.body.setAsync(content, { coercionType }, (result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          resolve(true);
        } else {
          reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to update Outlook body.'));
        }
      });
    });
  }

  global.OutlookAdapter = {
    getModeLabel,
    getSubject,
    getBody,
    setBody,
  };
})(typeof window !== 'undefined' ? window : globalThis);
