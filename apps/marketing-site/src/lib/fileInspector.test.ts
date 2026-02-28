// TEAM_152: Tests for file inspector utilities
// TEAM_241: Added image file tests
import {
  isTextFile,
  isPdfFile,
  isImageFile,
  formatFileSize,
  validateFile,
  SUPPORTED_EXTENSIONS,
  SUPPORTED_IMAGE_EXTENSIONS,
  SUPPORTED_MIME_TYPES,
  MAX_FILE_SIZE_BYTES,
  IMAGE_MAX_SIZE_BYTES,
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
      expect(isTextFile("video.mp4", "video/mp4")).toBe(false);
      expect(isTextFile("archive.zip", "application/zip")).toBe(false);
      expect(isTextFile("binary.exe", "application/octet-stream")).toBe(false);
    });

    it("returns false for image files (images are handled separately)", () => {
      expect(isTextFile("image.png", "image/png")).toBe(false);
      expect(isTextFile("photo.jpg", "image/jpeg")).toBe(false);
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
      const result = validateFile("video.mp4", "video/mp4", 1024);
      expect(result.valid).toBe(false);
      if (!result.valid) {
        expect(result.reason).toContain("Unsupported file type");
        expect(result.reason).toContain("video.mp4");
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
    it("has a reasonable max file size for text", () => {
      expect(MAX_FILE_SIZE_BYTES).toBe(5 * 1024 * 1024);
    });

    it("has a 10 MB max file size for images", () => {
      expect(IMAGE_MAX_SIZE_BYTES).toBe(10 * 1024 * 1024);
    });

    it("includes common text extensions", () => {
      expect(SUPPORTED_EXTENSIONS).toContain(".txt");
      expect(SUPPORTED_EXTENSIONS).toContain(".md");
      expect(SUPPORTED_EXTENSIONS).toContain(".json");
      expect(SUPPORTED_EXTENSIONS).toContain(".py");
      expect(SUPPORTED_EXTENSIONS).toContain(".js");
      expect(SUPPORTED_EXTENSIONS).toContain(".ts");
    });

    it("includes image extensions", () => {
      expect(SUPPORTED_EXTENSIONS).toContain(".jpg");
      expect(SUPPORTED_EXTENSIONS).toContain(".jpeg");
      expect(SUPPORTED_EXTENSIONS).toContain(".png");
      expect(SUPPORTED_EXTENSIONS).toContain(".webp");
      expect(SUPPORTED_IMAGE_EXTENSIONS).toContain(".jpg");
      expect(SUPPORTED_IMAGE_EXTENSIONS).toContain(".png");
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

    it("includes image MIME types", () => {
      expect(SUPPORTED_MIME_TYPES).toContain("image/jpeg");
      expect(SUPPORTED_MIME_TYPES).toContain("image/png");
      expect(SUPPORTED_MIME_TYPES).toContain("image/webp");
    });

    it("has a display string for supported formats including images", () => {
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("JPEG");
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("PNG");
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("WebP");
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("PDF");
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("TXT");
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("JSON");
      expect(SUPPORTED_FORMATS_DISPLAY).toContain("PY");
    });
  });
});

describe("isImageFile", () => {
  it("detects JPEG by MIME type", () => {
    expect(isImageFile("photo.jpg", "image/jpeg")).toBe(true);
    expect(isImageFile("photo.jpeg", "image/jpeg")).toBe(true);
  });

  it("detects PNG by MIME type", () => {
    expect(isImageFile("image.png", "image/png")).toBe(true);
  });

  it("detects WebP by MIME type", () => {
    expect(isImageFile("image.webp", "image/webp")).toBe(true);
  });

  it("detects JPEG by extension when MIME is generic", () => {
    expect(isImageFile("photo.jpg", "application/octet-stream")).toBe(true);
    expect(isImageFile("photo.jpeg", "")).toBe(true);
  });

  it("detects PNG by extension", () => {
    expect(isImageFile("image.PNG", "")).toBe(true);
  });

  it("returns false for text files", () => {
    expect(isImageFile("readme.txt", "text/plain")).toBe(false);
    expect(isImageFile("data.json", "application/json")).toBe(false);
  });

  it("returns false for PDF", () => {
    expect(isImageFile("doc.pdf", "application/pdf")).toBe(false);
  });
});

describe("isTextFile with images excluded", () => {
  it("returns false for image MIME types", () => {
    expect(isTextFile("photo.jpg", "image/jpeg")).toBe(false);
    expect(isTextFile("image.png", "image/png")).toBe(false);
  });

  it("returns false for image extensions even with generic MIME", () => {
    expect(isTextFile("photo.jpg", "application/octet-stream")).toBe(false);
    expect(isTextFile("image.png", "")).toBe(false);
  });
});

describe("validateFile with images", () => {
  it("accepts valid JPEG files", () => {
    const result = validateFile("photo.jpg", "image/jpeg", 1024);
    expect(result).toEqual({ valid: true });
  });

  it("accepts valid PNG files", () => {
    const result = validateFile("image.png", "image/png", 2048);
    expect(result).toEqual({ valid: true });
  });

  it("accepts images up to 10 MB", () => {
    const result = validateFile("photo.jpg", "image/jpeg", IMAGE_MAX_SIZE_BYTES);
    expect(result).toEqual({ valid: true });
  });

  it("rejects images over 10 MB", () => {
    const result = validateFile("huge.jpg", "image/jpeg", IMAGE_MAX_SIZE_BYTES + 1);
    expect(result.valid).toBe(false);
    if (!result.valid) {
      expect(result.reason).toContain("File too large");
    }
  });

  it("uses 5 MB limit for text files (not 10 MB)", () => {
    // 6 MB text file should be rejected
    const result = validateFile("big.txt", "text/plain", 6 * 1024 * 1024);
    expect(result.valid).toBe(false);
    // 6 MB image should be accepted
    const imgResult = validateFile("big.jpg", "image/jpeg", 6 * 1024 * 1024);
    expect(imgResult.valid).toBe(true);
  });

  it("rejects unsupported file types with appropriate message", () => {
    const result = validateFile("video.mp4", "video/mp4", 1024);
    expect(result.valid).toBe(false);
    if (!result.valid) {
      expect(result.reason).toContain("image");
    }
  });
});
