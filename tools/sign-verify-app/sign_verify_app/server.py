# TEAM_158: FastAPI server for sign & verify test app
"""
Local test app: drop an unsigned PDF → sign it → verify it.

Endpoints:
    GET  /           — Serves the single-page UI
    POST /api/sign   — Upload PDF, sign via enterprise API, return signed PDF + metadata
    POST /api/verify — Upload PDF, verify via verification service, return results
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
from pathlib import Path

import fitz
import httpx
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from xml_to_pdf.sign_existing import (
    SignExistingError,
    extract_text_from_pdf,
    sign_existing_pdf,
)
from xml_to_pdf.signer import EMBEDDING_MODES, SigningError

app = FastAPI(title="Sign & Verify Test App", version="0.1.0")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

VERIFICATION_SERVICE_URL = os.environ.get(
    "VERIFICATION_SERVICE_URL", "http://localhost:8000"
)
ENTERPRISE_API_URL = os.environ.get("ENCYPHER_API_URL", "http://localhost:8000")


# ---------------------------------------------------------------------------
# API: Sign
# ---------------------------------------------------------------------------


@app.post("/api/sign")
async def sign_pdf_endpoint(
    file: UploadFile = File(...),
    mode: str = Form("minimal"),
    title: str = Form(""),
):
    """Sign an uploaded PDF and return the signed PDF + metadata."""
    if mode not in EMBEDDING_MODES:
        return JSONResponse(
            {"error": f"Invalid mode '{mode}'. Valid: {list(EMBEDDING_MODES.keys())}"},
            status_code=400,
        )

    # Write uploaded PDF to temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_in:
        content = await file.read()
        tmp_in.write(content)
        tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path.replace(".pdf", "_signed.pdf")

    try:
        result = sign_existing_pdf(
            tmp_in_path,
            tmp_out_path,
            mode=mode,
            document_title=title or None,
            api_key=os.environ.get("ENCYPHER_API_KEY"),
        )

        signed_bytes = Path(tmp_out_path).read_bytes()
        signed_b64 = base64.b64encode(signed_bytes).decode("ascii")

        # Count invisible chars
        visible = sum(
            1 for c in result.signed_text if c.isprintable() or c in "\n\r\t"
        )
        invisible = len(result.signed_text) - visible

        return JSONResponse(
            {
                "success": True,
                "signed_pdf_base64": signed_b64,
                "signed_pdf_size": len(signed_bytes),
                "original_size": len(content),
                "document_id": result.document_id,
                "mode": mode,
                "mode_label": EMBEDDING_MODES[mode]["label"],
                "total_segments": result.total_segments,
                "signed_text_length": len(result.signed_text),
                "invisible_chars": invisible,
                "overhead_percent": f"{invisible / visible * 100:.1f}%" if visible else "0%",
                "instance_id": result.instance_id,
                "merkle_root": result.merkle_root,
                "verification_url": result.verification_url,
            }
        )
    except (SignExistingError, SigningError) as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"Unexpected error: {e}"}, status_code=500)
    finally:
        Path(tmp_in_path).unlink(missing_ok=True)
        Path(tmp_out_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_encypher_signed_text(pdf_path: str) -> str | None:
    """
    Extract the EncypherSignedText metadata stream from a PDF catalog.

    Returns the UTF-8 signed text if found, or None if the stream is absent.
    """
    doc = fitz.open(pdf_path)
    try:
        cat = doc.pdf_catalog()
        result = doc.xref_get_key(cat, "EncypherSignedText")
        if result[0] != "xref":
            return None
        ref_xref = int(result[1].split()[0])
        stream_data = doc.xref_stream(ref_xref)
        return stream_data.decode("utf-8")
    except Exception:
        return None
    finally:
        doc.close()


# ---------------------------------------------------------------------------
# API: Verify
# ---------------------------------------------------------------------------


@app.post("/api/verify")
async def verify_pdf_endpoint(file: UploadFile = File(...)):
    """Verify an uploaded PDF via the verification service."""
    content = await file.read()

    # Write to temp file to extract text
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # TEAM_158: Prefer the EncypherSignedText metadata stream (lossless
        # copy of signed text with invisible chars) over raw page text.
        text = _extract_encypher_signed_text(tmp_path)
        if not text:
            text = extract_text_from_pdf(tmp_path)
    except SignExistingError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # Send to verification service
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{VERIFICATION_SERVICE_URL}/api/v1/verify",
                json={"text": text},
            )
        data = resp.json()

        if resp.status_code != 200:
            return JSONResponse(
                {
                    "error": f"Verification service returned {resp.status_code}",
                    "detail": data,
                },
                status_code=502,
            )

        # Extract the useful fields
        result_data = data.get("data", data)
        return JSONResponse(
            {
                "success": True,
                "verification_status": result_data.get("verification_status", "Unknown"),
                "valid": result_data.get("valid", False),
                "tampered": result_data.get("tampered", False),
                "reason_code": result_data.get("reason_code", "Unknown"),
                "signer_id": result_data.get("signer_id"),
                "signer_name": result_data.get("signer_name"),
                "timestamp": result_data.get("timestamp"),
                "details": result_data.get("details"),
                "embeddings_found": result_data.get("embeddings_found", 0),
                "all_embeddings": result_data.get("all_embeddings"),
            }
        )
    except httpx.RequestError as e:
        return JSONResponse(
            {"error": f"Cannot reach verification service: {e}"},
            status_code=502,
        )
    except Exception as e:
        return JSONResponse({"error": f"Unexpected error: {e}"}, status_code=500)


# ---------------------------------------------------------------------------
# API: Modes
# ---------------------------------------------------------------------------


@app.get("/api/modes")
async def get_modes():
    return JSONResponse(
        {
            mode: {"label": cfg["label"], "manifest_mode": cfg["manifest_mode"]}
            for mode, cfg in EMBEDDING_MODES.items()
        }
    )


# ---------------------------------------------------------------------------
# UI: Single-page HTML app
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def index():
    return _build_html()


def _build_html() -> str:
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Encypher Sign & Verify</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config={darkMode:'class',theme:{extend:{colors:{brand:'#6366f1'}}}}</script>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  .drop-active { border-color: #6366f1 !important; background: rgba(99,102,241,0.08) !important; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner { animation: spin 1s linear infinite; }
</style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen">
<div id="app" class="max-w-3xl mx-auto px-4 py-8">

  <!-- Header -->
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-white mb-1">Sign & Verify</h1>
    <p class="text-gray-400 text-sm">Drop an unsigned PDF to sign it with EncypherAI provenance, then verify the result.</p>
  </div>

  <!-- Step indicator -->
  <div id="steps" class="flex items-center gap-2 mb-6 text-sm">
    <span id="step1" class="px-3 py-1 rounded-full bg-indigo-600 text-white font-medium">1. Upload PDF</span>
    <span class="text-gray-600">→</span>
    <span id="step2" class="px-3 py-1 rounded-full bg-gray-800 text-gray-400">2. Sign</span>
    <span class="text-gray-600">→</span>
    <span id="step3" class="px-3 py-1 rounded-full bg-gray-800 text-gray-400">3. Verify</span>
  </div>

  <!-- Drop zone -->
  <div id="dropzone" class="border-2 border-dashed border-gray-700 rounded-xl p-12 text-center cursor-pointer hover:border-gray-500 transition-colors mb-6">
    <svg class="mx-auto mb-4 opacity-50" width="48" height="48" viewBox="0 0 48 48" fill="none"><rect x="8" y="4" width="32" height="40" rx="3" stroke="currentColor" stroke-width="1.5"/><path d="M16 18h16M16 24h16M16 30h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    <p class="text-lg font-medium mb-1" id="dropLabel">Drop a PDF here or click to browse</p>
    <p class="text-sm text-gray-500">Supports any PDF file</p>
    <input type="file" id="fileInput" accept=".pdf" class="hidden">
  </div>

  <!-- File info + mode selector (hidden until file selected) -->
  <div id="fileInfo" class="hidden mb-6">
    <div class="flex items-center justify-between p-4 bg-gray-900 rounded-lg border border-gray-800 mb-4">
      <div class="flex items-center gap-3">
        <span class="text-2xl">📕</span>
        <div>
          <p class="font-medium" id="fileName"></p>
          <p class="text-xs text-gray-400" id="fileSize"></p>
        </div>
      </div>
      <button onclick="resetAll()" class="text-sm text-gray-400 hover:text-white px-3 py-1 rounded border border-gray-700 hover:border-gray-500">Clear</button>
    </div>

    <div class="flex items-end gap-3 mb-4">
      <div class="flex-1">
        <label class="block text-sm font-medium text-gray-300 mb-1">Signing Mode</label>
        <select id="modeSelect" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none">
          <option value="minimal">Minimal UUID per-sentence</option>
          <option value="zw_sentence">ZW embedding (sentence-level)</option>
          <option value="zw_document">ZW embedding (document-level)</option>
          <option value="c2pa_full">Default C2PA (full manifest)</option>
          <option value="lightweight">Lightweight UUID manifest</option>
        </select>
      </div>
      <button id="signBtn" onclick="signPdf()" class="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg transition-colors">
        Sign PDF
      </button>
    </div>
  </div>

  <!-- Loading -->
  <div id="loading" class="hidden mb-6">
    <div class="flex items-center justify-center p-8 bg-gray-900 rounded-lg border border-gray-800">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full spinner mr-3"></div>
      <span id="loadingText" class="text-gray-300">Signing PDF...</span>
    </div>
  </div>

  <!-- Sign result -->
  <div id="signResult" class="hidden mb-6">
    <div class="p-4 bg-gray-900 rounded-lg border border-gray-800">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-semibold text-green-400 flex items-center gap-2">
          <span>✅</span> PDF Signed Successfully
        </h3>
        <div class="flex gap-2">
          <button onclick="downloadSigned()" class="text-sm px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded border border-gray-700">
            ⬇ Download
          </button>
          <button id="verifyBtn" onclick="verifyPdf()" class="text-sm px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-medium">
            Verify →
          </button>
        </div>
      </div>
      <div id="signDetails" class="grid grid-cols-2 gap-2 text-sm"></div>
    </div>
  </div>

  <!-- Verify result -->
  <div id="verifyResult" class="hidden mb-6"></div>

  <!-- Error -->
  <div id="errorBox" class="hidden mb-6">
    <div class="p-4 bg-red-950 border border-red-800 rounded-lg">
      <p class="text-red-300 font-medium mb-1">Error</p>
      <p class="text-red-200 text-sm" id="errorText"></p>
    </div>
  </div>

</div>

<script>
// State
let currentFile = null;
let signedPdfB64 = null;
let signedFileName = '';

// DOM refs
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const loading = document.getElementById('loading');
const signResult = document.getElementById('signResult');
const verifyResult = document.getElementById('verifyResult');
const errorBox = document.getElementById('errorBox');

// Drop zone events
dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.classList.add('drop-active'); });
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drop-active'));
dropzone.addEventListener('drop', e => {
  e.preventDefault();
  dropzone.classList.remove('drop-active');
  if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', e => {
  if (e.target.files.length) handleFile(e.target.files[0]);
});

function handleFile(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    showError('Please select a PDF file.');
    return;
  }
  currentFile = file;
  signedPdfB64 = null;
  document.getElementById('fileName').textContent = file.name;
  document.getElementById('fileSize').textContent = formatSize(file.size);
  dropzone.classList.add('hidden');
  fileInfo.classList.remove('hidden');
  signResult.classList.add('hidden');
  verifyResult.classList.add('hidden');
  errorBox.classList.add('hidden');
  setStep(1);
}

async function signPdf() {
  if (!currentFile) return;
  showLoading('Signing PDF...');
  setStep(2);
  errorBox.classList.add('hidden');
  signResult.classList.add('hidden');
  verifyResult.classList.add('hidden');

  const form = new FormData();
  form.append('file', currentFile);
  form.append('mode', document.getElementById('modeSelect').value);

  try {
    const resp = await fetch('/api/sign', { method: 'POST', body: form });
    const data = await resp.json();
    hideLoading();

    if (!data.success) {
      showError(data.error || 'Signing failed');
      return;
    }

    signedPdfB64 = data.signed_pdf_base64;
    signedFileName = currentFile.name.replace('.pdf', '_signed.pdf');

    const details = document.getElementById('signDetails');
    details.innerHTML = [
      ['Mode', data.mode_label],
      ['Document ID', '<code class="text-xs bg-gray-800 px-1 rounded">' + data.document_id + '</code>'],
      ['Segments', data.total_segments],
      ['Signed Text', data.signed_text_length.toLocaleString() + ' chars'],
      ['Invisible Chars', data.invisible_chars.toLocaleString() + ' (' + data.overhead_percent + ' overhead)'],
      ['Signed PDF Size', formatSize(data.signed_pdf_size)],
      ...(data.instance_id ? [['Instance ID', '<code class="text-xs bg-gray-800 px-1 rounded">' + data.instance_id + '</code>']] : []),
    ].map(([k, v]) => '<div class="text-gray-400">' + k + '</div><div class="text-gray-200">' + v + '</div>').join('');

    signResult.classList.remove('hidden');
    setStep(2);
  } catch (e) {
    hideLoading();
    showError('Network error: ' + e.message);
  }
}

async function verifyPdf() {
  if (!signedPdfB64) return;
  showLoading('Verifying signed PDF...');
  setStep(3);
  verifyResult.classList.add('hidden');
  errorBox.classList.add('hidden');

  // Convert base64 to blob for upload
  const bytes = Uint8Array.from(atob(signedPdfB64), c => c.charCodeAt(0));
  const blob = new Blob([bytes], { type: 'application/pdf' });
  const form = new FormData();
  form.append('file', blob, signedFileName);

  try {
    const resp = await fetch('/api/verify', { method: 'POST', body: form });
    const data = await resp.json();
    hideLoading();

    if (data.error) {
      showError(data.error);
      return;
    }

    const isValid = data.valid === true;
    const statusClass = isValid ? 'border-green-700 bg-green-950' : 'border-red-700 bg-red-950';
    const statusIcon = isValid ? '✅' : '❌';
    const statusText = isValid ? 'Verified Authentic' : 'Verification Failed';
    const statusDesc = isValid
      ? 'The signed PDF is authentic and has not been modified.'
      : (data.reason_code || 'Verification failed');

    let html = '<div class="p-4 rounded-lg border ' + statusClass + '">';
    html += '<h3 class="font-semibold text-lg flex items-center gap-2 mb-3">' + statusIcon + ' ' + statusText + '</h3>';
    html += '<p class="text-sm text-gray-300 mb-3">' + statusDesc + '</p>';
    html += '<div class="grid grid-cols-2 gap-2 text-sm">';

    const fields = [
      ['Status', data.verification_status],
      ['Valid', String(data.valid)],
      ['Reason Code', data.reason_code],
      ...(data.signer_name ? [['Signer', data.signer_name]] : []),
      ...(data.signer_id ? [['Signer ID', data.signer_id]] : []),
      ...(data.timestamp ? [['Timestamp', new Date(data.timestamp).toLocaleString()]] : []),
      ...(data.embeddings_found ? [['Embeddings Found', data.embeddings_found]] : []),
    ];
    fields.forEach(([k, v]) => {
      html += '<div class="text-gray-400">' + k + '</div><div class="text-gray-200">' + v + '</div>';
    });
    html += '</div>';

    if (data.all_embeddings && data.all_embeddings.length > 0) {
      html += '<div class="mt-3 pt-3 border-t border-gray-700">';
      html += '<p class="text-sm font-medium text-gray-300 mb-2">Embeddings (' + data.all_embeddings.length + ')</p>';
      html += '<div class="max-h-48 overflow-y-auto space-y-1">';
      data.all_embeddings.forEach((emb, i) => {
        const eIcon = emb.verdict?.valid ? '✅' : '❌';
        const eBg = emb.verdict?.valid ? 'bg-green-900/30 border-green-800' : 'bg-red-900/30 border-red-800';
        html += '<div class="text-xs p-2 rounded border ' + eBg + '">';
        html += eIcon + ' Embedding #' + emb.index;
        if (emb.verdict?.reason_code) html += ' — ' + emb.verdict.reason_code;
        html += '</div>';
      });
      html += '</div></div>';
    }

    if (data.details) {
      html += '<details class="mt-3 pt-3 border-t border-gray-700"><summary class="text-sm text-gray-400 cursor-pointer hover:text-gray-200">Raw Details</summary>';
      html += '<pre class="mt-2 text-xs bg-gray-900 p-3 rounded overflow-x-auto">' + JSON.stringify(data.details, null, 2) + '</pre>';
      html += '</details>';
    }

    html += '</div>';

    // Add "Start Over" button
    html += '<div class="mt-4 text-center"><button onclick="resetAll()" class="text-sm px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded border border-gray-700">Start Over</button></div>';

    verifyResult.innerHTML = html;
    verifyResult.classList.remove('hidden');
  } catch (e) {
    hideLoading();
    showError('Network error: ' + e.message);
  }
}

function downloadSigned() {
  if (!signedPdfB64) return;
  const bytes = Uint8Array.from(atob(signedPdfB64), c => c.charCodeAt(0));
  const blob = new Blob([bytes], { type: 'application/pdf' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = signedFileName;
  a.click();
  URL.revokeObjectURL(url);
}

function resetAll() {
  currentFile = null;
  signedPdfB64 = null;
  fileInput.value = '';
  dropzone.classList.remove('hidden');
  fileInfo.classList.add('hidden');
  signResult.classList.add('hidden');
  verifyResult.classList.add('hidden');
  errorBox.classList.add('hidden');
  hideLoading();
  setStep(1);
}

function showLoading(text) {
  document.getElementById('loadingText').textContent = text;
  loading.classList.remove('hidden');
}
function hideLoading() { loading.classList.add('hidden'); }

function showError(msg) {
  document.getElementById('errorText').textContent = msg;
  errorBox.classList.remove('hidden');
}

function setStep(n) {
  [1,2,3].forEach(i => {
    const el = document.getElementById('step' + i);
    if (i <= n) {
      el.className = 'px-3 py-1 rounded-full font-medium ' + (i === n ? 'bg-indigo-600 text-white' : 'bg-indigo-900 text-indigo-300');
    } else {
      el.className = 'px-3 py-1 rounded-full bg-gray-800 text-gray-400';
    }
  });
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
</script>
</body>
</html>"""


def main():
    port = int(os.environ.get("PORT", "8200"))
    print(f"Starting Sign & Verify app on http://localhost:{port}")
    print(f"  Verification service: {VERIFICATION_SERVICE_URL}")
    print(f"  Enterprise API: {ENTERPRISE_API_URL}")
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
