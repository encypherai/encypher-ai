//! Encypher SDK - Rust client for the Encypher Enterprise API.
//!
//! This is an auto-generated SDK. For the source, see:
//! <https://github.com/encypherai/encypherai-commercial/tree/main/sdk>
//!
//! # Usage
//!
//! ```rust
//! use encypher::Client;
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let client = Client::new("your_api_key");
//!     let result = client.sign("Hello, world!").await?;
//!     println!("{}", result.signed_text);
//!     Ok(())
//! }
//! ```

use crate::apis::configuration::Configuration;
use crate::apis::signing_api;
use crate::apis::verification_api;
use crate::models::{SignRequest, VerifyRequest};

/// High-level client for the Encypher Enterprise API.
pub struct Client {
    config: Configuration,
}

impl Client {
    /// Create a new Encypher client.
    pub fn new(api_key: &str) -> Self {
        Self::with_base_url(api_key, "https://api.encypherai.com")
    }

    /// Create a new Encypher client with a custom base URL.
    pub fn with_base_url(api_key: &str, base_url: &str) -> Self {
        let mut config = Configuration::new();
        config.base_path = base_url.to_string();
        config.bearer_access_token = Some(api_key.to_string());
        Self { config }
    }

    /// Sign content with a C2PA manifest.
    pub async fn sign(&self, text: &str) -> Result<crate::models::SignResponse, crate::apis::Error<signing_api::SignContentApiV1SignPostError>> {
        let request = SignRequest::new(text.to_string());
        signing_api::sign_content_api_v1_sign_post(&self.config, request).await
    }

    /// Verify signed content.
    pub async fn verify(&self, text: &str) -> Result<crate::models::VerifyResponse, crate::apis::Error<verification_api::VerifyContentApiV1VerifyPostError>> {
        let request = VerifyRequest::new(text.to_string());
        verification_api::verify_content_api_v1_verify_post(&self.config, request).await
    }
}
