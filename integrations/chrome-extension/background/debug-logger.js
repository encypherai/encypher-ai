/**
 * Encypher Debug Logger
 * 
 * Structured logging for the Chrome extension that activates automatically
 * when the API is pointed at localhost. Logs are stored in chrome.storage.local
 * and can be viewed in the popup's Debug tab.
 * 
 * TEAM_151: Added for localhost development debugging
 */

const DEBUG_LOG_KEY = 'encypher_debug_logs';
const MAX_LOGS = 500;

/**
 * Check if we're in dev mode (API pointed at localhost)
 */
async function isDevMode() {
  try {
    const result = await chrome.storage.sync.get({
      apiBaseUrl: 'https://api.encypherai.com',
      customApiUrl: ''
    });
    const url = result.apiBaseUrl === 'custom' ? result.customApiUrl : result.apiBaseUrl;
    return url.includes('localhost') || url.includes('127.0.0.1');
  } catch {
    return false;
  }
}

/**
 * Log levels with numeric priority
 */
const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  API: 4,    // API request/response
  MSG: 5,    // Chrome message passing
};

/**
 * Add a log entry (only when in dev mode)
 */
async function addLog(level, category, message, data = null) {
  if (!await isDevMode()) return;

  const entry = {
    id: `${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
    timestamp: new Date().toISOString(),
    level,
    category,
    message,
    data: data ? JSON.parse(JSON.stringify(data, truncateReplacer())) : null,
  };

  // Also log to the real console for service worker inspection
  const consoleMethod = level === 'ERROR' ? 'error' : level === 'WARN' ? 'warn' : 'log';
  console[consoleMethod](`[Encypher:${level}:${category}]`, message, data || '');

  try {
    const result = await chrome.storage.local.get({ [DEBUG_LOG_KEY]: [] });
    const logs = result[DEBUG_LOG_KEY];
    logs.push(entry);

    // Trim to max size
    while (logs.length > MAX_LOGS) {
      logs.shift();
    }

    await chrome.storage.local.set({ [DEBUG_LOG_KEY]: logs });
  } catch (e) {
    console.warn('Debug logger storage error:', e.message);
  }
}

/**
 * JSON replacer that truncates long strings to keep storage manageable
 */
function truncateReplacer(maxLen = 500) {
  return (key, value) => {
    if (typeof value === 'string' && value.length > maxLen) {
      return value.substring(0, maxLen) + `...[truncated ${value.length - maxLen} chars]`;
    }
    return value;
  };
}

/**
 * Get all stored logs
 */
async function getLogs() {
  try {
    const result = await chrome.storage.local.get({ [DEBUG_LOG_KEY]: [] });
    return result[DEBUG_LOG_KEY];
  } catch {
    return [];
  }
}

/**
 * Clear all stored logs
 */
async function clearLogs() {
  try {
    await chrome.storage.local.set({ [DEBUG_LOG_KEY]: [] });
  } catch {
    // ignore
  }
}

// Convenience methods
const debugLog = {
  debug: (category, message, data) => addLog('DEBUG', category, message, data),
  info: (category, message, data) => addLog('INFO', category, message, data),
  warn: (category, message, data) => addLog('WARN', category, message, data),
  error: (category, message, data) => addLog('ERROR', category, message, data),
  api: (category, message, data) => addLog('API', category, message, data),
  msg: (category, message, data) => addLog('MSG', category, message, data),
  getLogs,
  clearLogs,
  isDevMode,
};

export { debugLog, addLog, getLogs, clearLogs, isDevMode, LOG_LEVELS };
export default debugLog;
