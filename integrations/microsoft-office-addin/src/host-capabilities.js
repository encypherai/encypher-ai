const HOST_CAPABILITIES = {
  Word: {
    host: 'Word',
    canReadSelection: true,
    canReplaceSelection: true,
    canReadFullDocument: true,
    canReplaceFullDocument: true,
    notes: 'Uses Word.run for full-document operations.',
  },
  Excel: {
    host: 'Excel',
    canReadSelection: true,
    canReplaceSelection: true,
    canReadFullDocument: false,
    canReplaceFullDocument: false,
    notes: 'Selection-only support to avoid worksheet scope ambiguity.',
  },
  PowerPoint: {
    host: 'PowerPoint',
    canReadSelection: true,
    canReplaceSelection: true,
    canReadFullDocument: false,
    canReplaceFullDocument: false,
    notes: 'Selection-only support for cross-slide safety.',
  },
};

const DEFAULT_CAPABILITIES = {
  host: 'Unknown',
  canReadSelection: false,
  canReplaceSelection: false,
  canReadFullDocument: false,
  canReplaceFullDocument: false,
  notes: 'Unsupported host for this add-in workflow.',
};

function getHostCapabilities(hostName) {
  return HOST_CAPABILITIES[hostName] || DEFAULT_CAPABILITIES;
}

const HostCapabilities = {
  HOST_CAPABILITIES,
  DEFAULT_CAPABILITIES,
  getHostCapabilities,
};

if (typeof globalThis !== 'undefined') {
  globalThis.HostCapabilities = HostCapabilities;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = HostCapabilities;
}
