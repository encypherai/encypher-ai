// TEAM_152: Tests for file inspector utilities
import {
  isTextFile,
  isPdfFile,
  formatFileSize,
  validateFile,
  SUPPORTED_EXTENSIONS,
  SUPPORTED_MIME_TYPES,
  MAX_FILE_SIZE_BYTES,
  SUPPORTED_FORMATS_DISPLAY,
} from "./fileInspector";

describe("fileInspector", () => {
  describe("isTextFile", () => {
    it("accepts files with supported MIME types", () => {
      expect(isTextFile("doc.txt", "text/plain")).toBe(true);
      expect(isTextFile("page.html", "text/html")).toBe(true);
      expect(isTextFile("data.json", "application/json")).toBe(true);
      expect(isTextFile("style.css", "text/css")).toBe(true);
    });

    it("accepts files with text/* MIME type even if not explicitly listed", () => {
      expect(isTextFile("file.xyz", "text/x-custom")).toBe(true);
    });

    it("accepts files by extension when MIME type is empty or generic", () => {
      expect(isTextFile("script.py", "")).toBe(true);
      expect(isTextFile("code.rs", "application/octet-stream")).toBe(true);
      expect(isTextFile("readme.md", "")).toBe(true);
      expect(isTextFile("config.toml", "")).toBe(true);
      expect(isTextFile("query.sql", "")).toBe(true);
    });

    it("rejects files with unsupported extensions and no text MIME", () => {
      expect(isTextFile("image.png", "image/png")).toBe(false);
      expect(isTextFile("video.mp4", "video/mp4")).toBe(false);
      expect(isTextFile("archive.zip", "application/zip")).toBe(false);
      expect(isTextFile("binary.exe", "application/octet-stream")).toBe(false);
    });

    it("is case-insensitive for extensions", () => {
      expect(isTextFile("README.MD", "")).toBe(true);
      expect(isTextFile("script.PY", "")).toBe(true);
      expect(isTextFile("CODE.JS", "")).toBe(true);
    });

    it("accepts PDF files by MIME type", () => {
      expect(isTextFile("document.pdf", "application/pdf")).toBe(true);
    });

    it("accepts PDF files by extension", () => {
      expect(isTextFile("document.pdf", "")).toBe(true);
      expect(isTextFile("REPORT.PDF", "")).toBe(true);
    });
  });

  describe("isPdfFile", () => {
    it("detects PDF by MIME type", () => {
      expect(isPdfFile("file.pdf", "application/pdf")).toBe(true);
      expect(isPdfFile("file.txt", "application/pdf")).toBe(true);
    });

    it("detects PDF by extension", () => {
      expect(isPdfFile("document.pdf", "")).toBe(true);
      expect(isPdfFile("REPORT.PDF", "application/octet-stream")).toBe(true);
    });

    it("returns false for non-PDF files", () => {
      expect(isPdfFile("file.txt", "text/plain")).toBe(false);
      expect(isPdfFile("file.json", "application/json")).toBe(false);
    });
  });

  describe("formatFileSize", () => {
    it("formats bytes", () => {
      expect(formatFileSize(0)).toBe("0 B");
      expect(formatFileSize(512)).toBe("512 B");
      expect(formatFileSize(1023)).toBe("1023 B");
    });

    it("formats kilobytes", () => {
      expect(formatFileSize(1024)).toBe("1.0 KB");
      expect(formatFileSize(1536)).toBe("1.5 KB");
      expect(formatFileSize(10240)).toBe("10.0 KB");
    });

    it("formats megabytes", () => {
      expect(formatFileSize(1024 * 1024)).toBe("1.0 MB");
      expect(formatFileSize(5 * 1024 * 1024)).toBe("5.0 MB");
      expect(formatFileSize(2.5 * 1024 * 1024)).toBe("2.5 MB");
    });
  });

  describe("validateFile", () => {
    it("accepts valid text files", () => {
      const result = validateFile("readme.txt", "text/plain", 1024);
      expect(result).toEqual({ valid: true });
    });

    it("rejects unsupported file types", () => {
      const result = validateFile("image.png", "image/png", 1024);
      expect(result.valid).toBe(false);
      if (!result.valid) {
        expect(result.reason).toContain("Unsupported file type");
        expect(result.reason).toContain("image.png");
      }
    });

    it("rejects files exceeding size limit", () => {
      const result = validateFile("big.txt", "text/plain", MAX_FILE_SIZE_BYTES + 1);
      expect(result.valid).toBe(false);
      if (!result.valid) {
        expect(result.reason).toContain("File too large");
      }
    });

    it("accepts files at exactly the size limit", () => {
      const result = validateFile("exact.txt", "text/plain", MAX_FILE_SIZE_BYTES);
      expect(result).toEqual({ valid: true });
    });

    it("rejects empty files", () => {
      const result = validateFile("empty.txt", "text/plain", 0);
      expect(result.valid).toBe(false);
      if (!result.valid) {
        expect(result.reason).toContain("empty");
      }
    });

    it("accepts valid PDF files", () => {
      const result = validateFile("report.pdf", "application/pdf", 2048);
      expect(result).toEqual({ valid: true });
    });

    it("rejects oversized PDF files", () => {
      const result = validateFile("huge.pdf", "application/pdf", MAX_FILE_SIZE_BYTES + 1);
      expect(result.valid).toBe(false);
      if (!result.valid) {
        expect(result.reason).toContain("File too large");
      }
    });
  });

  describe("constants", () => {
    it("has a reasonable max file size", () => {
      expect(MAX_FILE_SIZE_BYTES).toBe(5 * 1024 * 1024);
    });

    it("includes common text extensions", () => {
      expect(SUPPORTED_EXTENSIONS).toContain(".txt");
      expect(SUPPORTED_EXTENSIONS).toContain(".md");
      expect(SUPPORTED_EXTENSIONS).toContain(".json");
      expect(SUPPORTED_EXTENSIONS).toContain(".py");
      expect(SUPPORTED_EXTENSIONS).toContain(".js");
      expect(SUPPORTED_EXTENSIONS).toContain(".ts");
    });

    it("includes PDF extension and MIME type", () => {
      expect(SUPPORTED_EXTENSIONS).toContain(".pdf");
      expect(SUPPORTED_MIME_TYPES).toContain("application/pdf");
    });

    it("includes common MIME types", () => {
      expect(SUPPORTED_MIME_TYPES).toContain("text/plain");
      expect(SUPPORTED_MIME_TYPES).toContain("application/json");
      expect(SUPPORTED_MIME_TYPES).toContain("text/html");
    });

    it("has a display string for supported formats including PDF", () => {
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("PDF");
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("TXT");
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("JSON");
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("PY");
    });
  });
});
