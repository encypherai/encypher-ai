(function (global) {
  function getHostName() {
    if (!global.Office || !Office.context || !Office.context.host) {
      return 'Unknown';
    }
    return Office.context.host;
  }

  function readSelectionText() {
    return new Promise((resolve, reject) => {
      Office.context.document.getSelectedDataAsync(
        Office.CoercionType.Text,
        (result) => {
          if (result.status === Office.AsyncResultStatus.Succeeded) {
            resolve((result.value || '').toString());
          } else {
            reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to read selection.'));
          }
        }
      );
    });
  }

  function readSelectionOoxml() {
    return new Promise((resolve, reject) => {
      Office.context.document.getSelectedDataAsync(
        Office.CoercionType.Ooxml,
        (result) => {
          if (result.status === Office.AsyncResultStatus.Succeeded) {
            resolve((result.value || '').toString());
          } else {
            reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to read selection OOXML.'));
          }
        }
      );
    });
  }

  function replaceSelectionText(value) {
    return new Promise((resolve, reject) => {
      Office.context.document.setSelectedDataAsync(
        value,
        { coercionType: Office.CoercionType.Text },
        (result) => {
          if (result.status === Office.AsyncResultStatus.Succeeded) {
            resolve(true);
          } else {
            reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to replace selection.'));
          }
        }
      );
    });
  }

  async function readFullDocumentText() {
    const host = getHostName();
    if (host !== 'Word') {
      throw new Error('Full-document actions are currently supported only in Word.');
    }

    return Word.run(async (context) => {
      const body = context.document.body;
      body.load('text');
      await context.sync();
      return body.text || '';
    });
  }

  async function replaceFullDocumentText(value) {
    const host = getHostName();
    if (host !== 'Word') {
      throw new Error('Full-document actions are currently supported only in Word.');
    }

    return Word.run(async (context) => {
      context.document.body.clear();
      context.document.body.insertText(value, Word.InsertLocation.start);
      await context.sync();
      return true;
    });
  }

  async function readFullDocumentOoxml() {
    const host = getHostName();
    if (host !== 'Word') {
      throw new Error('OOXML full-document actions are currently supported only in Word.');
    }

    return Word.run(async (context) => {
      const ooxml = context.document.body.getOoxml();
      await context.sync();
      return ooxml.value || '';
    });
  }

  async function replaceFullDocumentOoxml(value) {
    const host = getHostName();
    if (host !== 'Word') {
      throw new Error('OOXML full-document actions are currently supported only in Word.');
    }

    return Word.run(async (context) => {
      context.document.body.insertOoxml(value, Word.InsertLocation.replace);
      await context.sync();
      return true;
    });
  }

  global.EncypherHostAdapter = {
    getHostName,
    readSelectionText,
    readSelectionOoxml,
    replaceSelectionText,
    readFullDocumentText,
    replaceFullDocumentText,
    readFullDocumentOoxml,
    replaceFullDocumentOoxml,
  };
})(typeof window !== 'undefined' ? window : globalThis);
