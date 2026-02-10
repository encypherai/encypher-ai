// TEAM_152: Shared utilities for the File Inspector tool

export const SUPPORTED_EXTENSIONS = [
  '.txt', '.md', '.html', '.htm', '.json', '.xml',
  '.csv', '.log', '.rtf', '.tex', '.yaml', '.yml',
  '.toml', '.ini', '.cfg', '.conf', '.py', '.js',
  '.ts', '.tsx', '.jsx', '.css', '.scss', '.sql',
  '.sh', '.bat', '.ps1', '.rb', '.go', '.rs',
  '.java', '.c', '.cpp', '.h', '.hpp', '.swift',
  '.pdf',
];

export const SUPPORTED_MIME_TYPES = [
  'text/plain', 'text/html', 'text/css', 'text/csv',
  'text/markdown', 'text/xml', 'text/yaml',
  'application/json', 'application/xml', 'application/xhtml+xml',
  'application/x-yaml', 'application/toml',
  'application/javascript', 'application/typescript',
  'application/pdf',
];

export const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB

export const SUPPORTED_FORMATS_DISPLAY =
  'PDF, TXT, MD, HTML, JSON, XML, CSV, LOG, RTF, TEX, YAML, TOML, INI, PY, JS, TS, TSX, JSX, CSS, SQL, SH, RB, GO, RS, JAVA, C, CPP, H, SWIFT';

export function isTextFile(fileName: string, mimeType: string): boolean {
  if (SUPPORTED_MIME_TYPES.some((mime) => mimeType.startsWith(mime))) {
    return true;
  }
  if (mimeType.startsWith('text/')) {
    return true;
  }
  const ext = '.' + fileName.split('.').pop()?.toLowerCase();
  return SUPPORTED_EXTENSIONS.includes(ext);
}

export function isPdfFile(fileName: string, mimeType: string): boolean {
  if (mimeType === 'application/pdf') return true;
  const ext = '.' + fileName.split('.').pop()?.toLowerCase();
  return ext === '.pdf';
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export type FileValidationResult =
  | { valid: true }
  | { valid: false; reason: string };

export function validateFile(
  fileName: string,
  mimeType: string,
  sizeBytes: number
): FileValidationResult {
  if (!isTextFile(fileName, mimeType)) {
    return { valid: false, reason: `Unsupported file type: "${fileName}". Please upload a text-based file.` };
  }
  if (sizeBytes > MAX_FILE_SIZE_BYTES) {
    return { valid: false, reason: `File too large (${formatFileSize(sizeBytes)}). Maximum size is ${formatFileSize(MAX_FILE_SIZE_BYTES)}.` };
  }
  if (sizeBytes === 0) {
    return { valid: false, reason: 'File is empty. Please upload a file with content.' };
  }
  return { valid: true };
}
