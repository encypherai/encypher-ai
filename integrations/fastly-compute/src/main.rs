//! Encypher CDN Provenance — Fastly Compute@Edge
//!
//! Intercepts image responses from the origin backend, looks up the
//! C2PA manifest URL via the Encypher API, and injects a
//! `C2PA-Manifest-URL` response header.
//!
//! ## Fastly service configuration
//!
//! Required backends:
//!   * `origin`         — Publisher's origin server (existing)
//!   * `encypher_api`   — `api.encypher.com` (add in Fastly console)
//!
//! Required Edge Dictionary:
//!   * Name: `encypher_config`
//!   * Keys:
//!     - `api_base_url`  — e.g. "https://api.encypher.com"
//!     - `cache_ttl_s`   — e.g. "3600"
//!
//! Deploy with: `fastly compute publish`

use fastly::http::{Method, StatusCode};
use fastly::{Error, Request, Response};

const BACKEND_ORIGIN: &str = "origin";
const BACKEND_ENCYPHER: &str = "encypher_api";
const DICT_CONFIG: &str = "encypher_config";

/// Image MIME type prefixes that trigger provenance lookup.
const IMAGE_CONTENT_TYPE_PREFIX: &[&str] = &[
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/avif",
    "image/tiff",
];

/// Strip Cloudflare-style `/cdn-cgi/image/{opts}/` transform prefix.
/// Fastly uses different transform paths but we handle both patterns.
fn canonical_url(url: &str) -> String {
    // Strip /cdn-cgi/image/{opts}/ prefix
    if let Some(idx) = url.find("/cdn-cgi/image/") {
        let rest = &url[idx + "/cdn-cgi/image/".len()..];
        if let Some(slash) = rest.find('/') {
            let after = &rest[slash + 1..];
            // after is either a full URL or a path
            if after.starts_with("http://") || after.starts_with("https://") {
                return after.to_string();
            }
            // Reconstruct with origin
            let origin_end = url.find("/cdn-cgi/").unwrap_or(url.len());
            return format!("{}/{}", &url[..origin_end], after);
        }
    }
    // Strip common image resize query params
    // (Fastly Image Optimizer uses ?width=, ?height=, ?format=, ?quality=)
    if let Some(q_pos) = url.find('?') {
        let base = &url[..q_pos];
        let query = &url[q_pos + 1..];
        let resize_params = ["width", "height", "format", "quality", "w", "h", "q", "fit", "auto"];
        let filtered: Vec<&str> = query.split('&')
            .filter(|kv| {
                let key = kv.split('=').next().unwrap_or("");
                !resize_params.contains(&key)
            })
            .collect();
        if filtered.is_empty() {
            return base.to_string();
        }
        return format!("{}?{}", base, filtered.join("&"));
    }
    url.to_string()
}

fn is_image_content_type(ct: &str) -> bool {
    let ct_lower = ct.to_lowercase();
    IMAGE_CONTENT_TYPE_PREFIX.iter().any(|prefix| ct_lower.starts_with(prefix))
}

#[fastly::main]
fn main(req: Request) -> Result<Response, Error> {
    // Forward request to origin
    let beresp = req.clone_without_body().send(BACKEND_ORIGIN)?;

    // Only process image responses
    let content_type = beresp
        .get_header_str("Content-Type")
        .unwrap_or("")
        .to_string();

    if !is_image_content_type(&content_type) {
        return Ok(beresp);
    }

    // Get config
    let dict = fastly::Dictionary::open(DICT_CONFIG);
    let api_base = dict
        .get("api_base_url")
        .unwrap_or_else(|| "https://api.encypher.com".to_string());

    // Build canonical URL
    let request_url = req.get_url_str().to_string();
    let canonical = canonical_url(&request_url);

    // Look up manifest from Encypher API
    let lookup_url = format!(
        "{}/api/v1/cdn/manifests/lookup?url={}",
        api_base,
        urlencoding::encode(&canonical)
    );

    let lookup_req = Request::get(&lookup_url)
        .with_header("Accept", "application/json")
        .with_header("User-Agent", "Encypher-Fastly-Worker/1.0");

    // Best-effort lookup — don't block image delivery if API is unavailable
    if let Ok(lookup_resp) = lookup_req.send(BACKEND_ENCYPHER) {
        if lookup_resp.get_status() == StatusCode::OK {
            if let Ok(body_str) = lookup_resp.into_body_str() {
                // Parse record_id from JSON: {"record_id": "...", "manifest_url": "..."}
                // Use simple string search to avoid pulling in a JSON library
                if let Some(record_id) = extract_json_string_field(&body_str, "record_id") {
                    let manifest_url = format!("{}/api/v1/cdn/manifests/{}", api_base, record_id);
                    let mut resp = beresp;
                    resp.set_header("C2PA-Manifest-URL", &manifest_url);
                    resp.set_header("X-Encypher-Provenance", "active");
                    return Ok(resp);
                }
            }
        }
    }

    Ok(beresp)
}

/// Extract a string field value from a JSON object string without a full parser.
/// Only handles simple flat objects with string values.
fn extract_json_string_field(json: &str, field: &str) -> Option<String> {
    let needle = format!("\"{}\"", field);
    let pos = json.find(&needle)?;
    let after_key = &json[pos + needle.len()..];
    // Skip whitespace and colon
    let colon_pos = after_key.find(':')?;
    let after_colon = after_key[colon_pos + 1..].trim_start();
    if !after_colon.starts_with('"') {
        return None;
    }
    let inner = &after_colon[1..];
    let end = inner.find('"')?;
    Some(inner[..end].to_string())
}
