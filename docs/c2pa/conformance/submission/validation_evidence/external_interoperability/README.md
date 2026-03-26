# External Interoperability Evidence

This directory contains the results of testing C2PA manifests from third-party
implementations against Encypher's verifier.

## Files

- `external_ingestion_results.json` -- consolidated verification results for
  all third-party sample files

## Sources Tested

The following third-party C2PA implementations were tested:

**Google Pixel Camera (Prod)**
Real device captures including standard photos, 50MP mode, Portrait, Panorama,
Burst, Action Pan, Video Snapshot, and Add Me composite captures.

**Google Photos (Prod)**
Magic Editor, Magic Eraser, Crop, Zoom Enhance, and other AI edit operations.

**NotebookLM (Prod)**
Infographic generation output.

**Veo, Imagen, and Nano Banana (Prod)**
Text-to-image, text-to-video, image-to-video, and NanoBananaPro outputs.

**YouTube (Prod)**
Inspiration thumbnail content.

**Pixel Recorder (Prod)**
Audio recordings with C2PA provenance.

## Verification Method

Each file was passed to the Encypher verify endpoint and the raw c2pa-python
Reader.  The per-file evidence JSON files record:
- Whether a manifest was detected
- Whether the signature was valid
- The claim generator string (identifies the signing implementation)
- Any validation errors or trust list results

## Scope

External verification tests that our verifier correctly ingests and validates
manifests produced by other C2PA implementations.  It does not test that those
implementations can ingest our manifests -- that cross-direction test would
require uploading our signed files to each vendor's verification tool.
