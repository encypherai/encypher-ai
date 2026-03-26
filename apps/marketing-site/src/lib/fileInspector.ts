// TEAM_152: Shared utilities for the File Inspector tool
// TEAM_280: Expanded to cover all C2PA media formats (image, audio, video)

// ---------------------------------------------------------------------------
// Extensions
// ---------------------------------------------------------------------------

export const SUPPORTED_TEXT_EXTENSIONS = [
  '.txt', '.md', '.html', '.htm', '.json', '.xml',
  '.csv', '.log', '.rtf', '.tex', '.yaml', '.yml',
  '.toml', '.ini', '.cfg', '.conf', '.py', '.js',
  '.ts', '.tsx', '.jsx', '.css', '.scss', '.sql',
  '.sh', '.bat', '.ps1', '.rb', '.go', '.rs',
  '.java', '.c', '.cpp', '.h', '.hpp', '.swift',
  '.pdf',
];

export const SUPPORTED_IMAGE_EXTENSIONS = [
  '.jpg', '.jpeg', '.png', '.webp', '.tiff', '.tif',
  '.gif', '.heic', '.heif', '.avif', '.svg', '.dng', '.jxl',
];

export const SUPPORTED_AUDIO_EXTENSIONS = [
  '.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.weba',
];

export const SUPPORTED_VIDEO_EXTENSIONS = [
  '.mp4', '.mov', '.avi', '.webm', '.mkv',
];

export const SUPPORTED_EXTENSIONS = [
  ...SUPPORTED_TEXT_EXTENSIONS,
  ...SUPPORTED_IMAGE_EXTENSIONS,
  ...SUPPORTED_AUDIO_EXTENSIONS,
  ...SUPPORTED_VIDEO_EXTENSIONS,
];

// ---------------------------------------------------------------------------
// MIME types
// ---------------------------------------------------------------------------

export const SUPPORTED_TEXT_MIME_TYPES = [
  'text/plain', 'text/html', 'text/css', 'text/csv',
  'text/markdown', 'text/xml', 'text/yaml',
  'application/json', 'application/xml', 'application/xhtml+xml',
  'application/x-yaml', 'application/toml',
  'application/javascript', 'application/typescript',
  'application/pdf',
];

export const SUPPORTED_IMAGE_MIME_TYPES = [
  'image/jpeg', 'image/png', 'image/webp', 'image/tiff',
  'image/gif', 'image/heic', 'image/heif', 'image/avif',
  'image/svg+xml', 'image/x-adobe-dng', 'image/jxl',
];

export const SUPPORTED_AUDIO_MIME_TYPES = [
  'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/wave', 'audio/x-wav',
  'audio/flac', 'audio/mp4', 'audio/x-m4a', 'audio/aac',
  'audio/ogg', 'audio/webm',
];

export const SUPPORTED_VIDEO_MIME_TYPES = [
  'video/mp4', 'video/quicktime', 'video/x-msvideo',
  'video/webm', 'video/x-matroska', 'video/ogg',
];

export const SUPPORTED_MIME_TYPES = [
  ...SUPPORTED_TEXT_MIME_TYPES,
  ...SUPPORTED_IMAGE_MIME_TYPES,
  ...SUPPORTED_AUDIO_MIME_TYPES,
  ...SUPPORTED_VIDEO_MIME_TYPES,
];

// ---------------------------------------------------------------------------
// Size limits
// ---------------------------------------------------------------------------

export const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;        // 5 MB (text/PDF)
export const IMAGE_MAX_SIZE_BYTES = 10 * 1024 * 1024;      // 10 MB
export const AUDIO_MAX_SIZE_BYTES = 25 * 1024 * 1024;      // 25 MB
export const VIDEO_MAX_SIZE_BYTES = 100 * 1024 * 1024;     // 100 MB

// ---------------------------------------------------------------------------
// Display
// ---------------------------------------------------------------------------

export const SUPPORTED_FORMATS_DISPLAY =
  'JPEG, PNG, WebP, TIFF, GIF, HEIC, HEIF, AVIF, SVG, DNG, JXL -- MP4, MOV, AVI, WebM -- MP3, WAV, FLAC, M4A, OGG, AAC -- PDF, TXT, MD, HTML, JSON, XML';

// ---------------------------------------------------------------------------
// Detection helpers
// ---------------------------------------------------------------------------

function getExtension(fileName: string): string {
  return '.' + (fileName.split('.').pop()?.toLowerCase() || '');
}

export function isImageFile(fileName: string, mimeType: string): boolean {
  if (SUPPORTED_IMAGE_MIME_TYPES.some((mime) => mimeType === mime)) return true;
  if (mimeType.startsWith('image/')) return true;
  return SUPPORTED_IMAGE_EXTENSIONS.includes(getExtension(fileName));
}

export function isAudioFile(fileName: string, mimeType: string): boolean {
  if (SUPPORTED_AUDIO_MIME_TYPES.some((mime) => mimeType === mime)) return true;
  if (mimeType.startsWith('audio/')) return true;
  return SUPPORTED_AUDIO_EXTENSIONS.includes(getExtension(fileName));
}

export function isVideoFile(fileName: string, mimeType: string): boolean {
  if (SUPPORTED_VIDEO_MIME_TYPES.some((mime) => mimeType === mime)) return true;
  if (mimeType.startsWith('video/')) return true;
  return SUPPORTED_VIDEO_EXTENSIONS.includes(getExtension(fileName));
}

export function isTextFile(fileName: string, mimeType: string): boolean {
  if (isImageFile(fileName, mimeType)) return false;
  if (isAudioFile(fileName, mimeType)) return false;
  if (isVideoFile(fileName, mimeType)) return false;
  if (SUPPORTED_TEXT_MIME_TYPES.some((mime) => mimeType.startsWith(mime))) return true;
  if (mimeType.startsWith('text/')) return true;
  return SUPPORTED_TEXT_EXTENSIONS.includes(getExtension(fileName));
}

export function isPdfFile(fileName: string, mimeType: string): boolean {
  if (mimeType === 'application/pdf') return true;
  return getExtension(fileName) === '.pdf';
}

export type FileKind = 'image' | 'audio' | 'video' | 'text';

export function getFileKind(fileName: string, mimeType: string): FileKind {
  if (isImageFile(fileName, mimeType)) return 'image';
  if (isAudioFile(fileName, mimeType)) return 'audio';
  if (isVideoFile(fileName, mimeType)) return 'video';
  return 'text';
}

// ---------------------------------------------------------------------------
// MIME type resolution (fallback when browser reports empty or generic type)
// ---------------------------------------------------------------------------

const EXTENSION_TO_MIME: Record<string, string> = {
  // Images
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
  '.webp': 'image/webp', '.tiff': 'image/tiff', '.tif': 'image/tiff',
  '.gif': 'image/gif', '.heic': 'image/heic', '.heif': 'image/heif',
  '.avif': 'image/avif', '.svg': 'image/svg+xml',
  '.dng': 'image/x-adobe-dng', '.jxl': 'image/jxl',
  // Audio
  '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.flac': 'audio/flac',
  '.m4a': 'audio/mp4', '.ogg': 'audio/ogg', '.aac': 'audio/aac',
  '.weba': 'audio/webm',
  // Video
  '.mp4': 'video/mp4', '.mov': 'video/quicktime', '.avi': 'video/x-msvideo',
  '.webm': 'video/webm', '.mkv': 'video/x-matroska',
};

export function resolveMimeType(fileName: string, browserMime: string): string {
  if (browserMime && browserMime !== 'application/octet-stream') return browserMime;
  return EXTENSION_TO_MIME[getExtension(fileName)] || browserMime || 'application/octet-stream';
}

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

export type FileValidationResult =
  | { valid: true }
  | { valid: false; reason: string };

export function validateFile(
  fileName: string,
  mimeType: string,
  sizeBytes: number
): FileValidationResult {
  const kind = getFileKind(fileName, mimeType);
  const isKnown = isImageFile(fileName, mimeType)
    || isAudioFile(fileName, mimeType)
    || isVideoFile(fileName, mimeType)
    || isTextFile(fileName, mimeType);

  if (!isKnown) {
    return {
      valid: false,
      reason: `Unsupported file type: "${fileName}". Supported: images, audio, video, and text-based files.`,
    };
  }

  const maxBytes = kind === 'video' ? VIDEO_MAX_SIZE_BYTES
    : kind === 'audio' ? AUDIO_MAX_SIZE_BYTES
    : kind === 'image' ? IMAGE_MAX_SIZE_BYTES
    : MAX_FILE_SIZE_BYTES;

  if (sizeBytes > maxBytes) {
    return {
      valid: false,
      reason: `File too large (${formatFileSize(sizeBytes)}). Maximum size for ${kind} files is ${formatFileSize(maxBytes)}.`,
    };
  }

  if (sizeBytes === 0) {
    return { valid: false, reason: 'File is empty. Please upload a file with content.' };
  }

  return { valid: true };
}
