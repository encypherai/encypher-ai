#!/usr/bin/env python3
"""
Generate SDKs from OpenAPI specification.

Usage:
    uv run python sdk/generate_sdk.py python      # Generate Python SDK
    uv run python sdk/generate_sdk.py typescript  # Generate TypeScript SDK
    uv run python sdk/generate_sdk.py go          # Generate Go SDK
    uv run python sdk/generate_sdk.py rust        # Generate Rust SDK
    uv run python sdk/generate_sdk.py all         # Generate all SDKs
"""
import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

SDK_DIR = Path(__file__).parent
OPENAPI_PUBLIC_SPEC = SDK_DIR / "openapi.public.json"
OPENAPI_INTERNAL_SPEC = SDK_DIR / "openapi.internal.json"
OPENAPI_SPEC = OPENAPI_PUBLIC_SPEC

MONOREPO_URL = "https://github.com/encypherai/encypherai-commercial"
MONOREPO_GIT_URL = "https://github.com/encypherai/encypherai-commercial.git"
GO_MODULE_PATH = "github.com/encypherai/encypherai-commercial/sdk/go"

PRODUCTION_BASE_URL = "https://api.encypherai.com"
LOCAL_DEV_BASE_URL = "http://localhost:8007"
GO_VERSION = "1.21"
HOMEPAGE_URL = "https://encypherai.com"

# Windows needs shell=True for npx
IS_WINDOWS = platform.system() == "Windows"

# Initialize console
console = Console() if RICH_AVAILABLE else None

# SDK configurations
SDK_CONFIGS = {
    "python": {
        "generator": "python",
        "emoji": "🐍",
        "name": "Python",
        "output_dir": "python",
        "additional_properties": {
            "packageName": "encypher",
            "projectName": "encypher",
            "packageUrl": "https://github.com/encypherai/encypherai-commercial/tree/main/sdk/python",
            "generateSourceCodeOnly": "false",
            "library": "urllib3",
        },
    },
    "typescript": {
        "generator": "typescript-fetch",
        "emoji": "📘",
        "name": "TypeScript",
        "output_dir": "typescript",
        "additional_properties": {
            "npmName": "@encypher/sdk",
            "supportsES6": "true",
            "typescriptThreePlus": "true",
            "withInterfaces": "true",
        },
    },
    "go": {
        "generator": "go",
        "emoji": "🐹",
        "name": "Go",
        "output_dir": "go",
        "additional_properties": {
            "packageName": "encypher",
            "isGoSubmodule": "true",
            "generateInterfaces": "true",
        },
    },
    "rust": {
        "generator": "rust",
        "emoji": "🦀",
        "name": "Rust",
        "output_dir": "rust",
        "additional_properties": {
            "packageName": "encypher",
            "library": "reqwest",
            "supportAsync": "true",
        },
    },
}


def log_info(msg: str):
    """Log info message."""
    if RICH_AVAILABLE:
        console.print(f"[blue]ℹ[/blue] {msg}")
    else:
        print(f"ℹ {msg}")


def log_success(msg: str):
    """Log success message."""
    if RICH_AVAILABLE:
        console.print(f"[green]✓[/green] {msg}")
    else:
        print(f"✓ {msg}")


def log_error(msg: str):
    """Log error message."""
    if RICH_AVAILABLE:
        console.print(f"[red]✗[/red] {msg}")
    else:
        print(f"✗ {msg}")


def log_warning(msg: str):
    """Log warning message."""
    if RICH_AVAILABLE:
        console.print(f"[yellow]⚠[/yellow] {msg}")
    else:
        print(f"⚠ {msg}")


def _write_if_changed(path: Path, content: str) -> None:
    existing = path.read_text(encoding="utf-8")
    if existing == content:
        return
    path.write_text(content, encoding="utf-8")


def _patch_python_metadata(output_dir: Path) -> None:
    pyproject_path = output_dir / "pyproject.toml"
    if pyproject_path.exists():
        text = pyproject_path.read_text(encoding="utf-8")
        text = re.sub(r'"([^"\s]+) \(([^\)]+)\)"', r'"\1\2"', text)

        authors_block = (
            'authors = [\n'
            '  {name = "Encypher", email = "sdk@encypherai.com"},\n'
            ']'
        )
        if re.search(r"(?ms)^authors\s*=\s*\[.*?\n\]\s*$", text):
            text = re.sub(r"(?ms)^authors\s*=\s*\[.*?\n\]\s*$", authors_block, text)
        else:
            match = re.search(r"(?ms)^\[project\]\n", text)
            if match:
                insert_at = match.end(0)
                text = text[:insert_at] + authors_block + "\n" + text[insert_at:]

        if "[project.urls]" not in text:
            text = text.rstrip() + "\n\n[project.urls]\n"

        def upsert_project_url(key: str, value: str) -> None:
            nonlocal text
            if re.search(rf"(?m)^{re.escape(key)}\s*=\s*\".*\"\s*$", text):
                text = re.sub(
                    rf"(?m)^{re.escape(key)}\s*=\s*\".*\"\s*$",
                    f'{key} = "{value}"',
                    text,
                )
                return

            match = re.search(r"(?ms)(\[project\.urls\]\n)", text)
            if match:
                insert_at = match.end(1)
                text = text[:insert_at] + f'{key} = "{value}"\n' + text[insert_at:]

        upsert_project_url("Homepage", HOMEPAGE_URL)
        upsert_project_url("Documentation", f"{PRODUCTION_BASE_URL}/docs")
        upsert_project_url("Repository", MONOREPO_URL)
        upsert_project_url("Changelog", f"{MONOREPO_URL}/releases")
        _write_if_changed(pyproject_path, text)

    setup_path = output_dir / "setup.py"
    if setup_path.exists():
        text = setup_path.read_text(encoding="utf-8")
        text = re.sub(r'(?m)^\s*author\s*=\s*".*"\s*,\s*$', '    author="Encypher",', text)
        text = re.sub(r'(?m)^\s*author_email\s*=\s*".*"\s*,\s*$', '    author_email="sdk@encypherai.com",', text)
        text = re.sub(r'(?m)^\s*url\s*=\s*".*"\s*,\s*$', f'    url="{MONOREPO_URL}",', text)
        _write_if_changed(setup_path, text)

    config_path = output_dir / "encypher" / "configuration.py"
    if config_path.exists():
        text = config_path.read_text(encoding="utf-8")
        text = text.replace('"http://localhost" if host is None else host', f'"{PRODUCTION_BASE_URL}" if host is None else host')
        pattern = r"(def get_host_settings\(self\)(?: -> List\[HostSetting\])?:\n(?:[ \t]+\"\"\"[\s\S]*?\"\"\"\n)?[ \t]+return \[)([\s\S]*?)(\n[ \t]+\]\n)"
        replacement_body = (
            "\n            {\n"
            f"                'url': \"{PRODUCTION_BASE_URL}\",\n"
            "                'description': \"Production\",\n"
            "            },\n"
            "            {\n"
            f"                'url': \"{LOCAL_DEV_BASE_URL}\",\n"
            "                'description': \"Local development\",\n"
            "            }"
        )
        text = re.sub(pattern, r"\1" + replacement_body + r"\3", text)
        _write_if_changed(config_path, text)


def _patch_typescript_metadata(output_dir: Path) -> None:
    package_json = output_dir / "package.json"
    if not package_json.exists():
        return
    data = json.loads(package_json.read_text(encoding="utf-8"))
    repo = data.get("repository")
    if not isinstance(repo, dict):
        repo = {}
        data["repository"] = repo
    repo["type"] = "git"
    repo["url"] = MONOREPO_GIT_URL
    repo["directory"] = "sdk/typescript"
    _write_if_changed(package_json, json.dumps(data, indent=2) + "\n")

    runtime_path = output_dir / "src" / "runtime.ts"
    if runtime_path.exists():
        text = runtime_path.read_text(encoding="utf-8")
        text = text.replace('"http://localhost"', f'"{PRODUCTION_BASE_URL}"')
        _write_if_changed(runtime_path, text)


def _patch_go_metadata(output_dir: Path) -> None:
    go_mod = output_dir / "go.mod"
    if go_mod.exists():
        text = go_mod.read_text(encoding="utf-8")
        text = re.sub(r'(?m)^module\s+\S+\s*$', f"module {GO_MODULE_PATH}", text)
        text = re.sub(r'(?m)^go\s+\S+\s*$', f"go {GO_VERSION}", text)
        _write_if_changed(go_mod, text)

    readme = output_dir / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        text = text.replace("github.com/encypherai/sdk-go", GO_MODULE_PATH)
        _write_if_changed(readme, text)

    main_go = output_dir / "cmd" / "encypher" / "main.go"
    if main_go.exists():
        text = main_go.read_text(encoding="utf-8")
        text = text.replace("github.com/encypherai/sdk-go", GO_MODULE_PATH)
        if not text.strip():
            text = "package main\n\nfunc main() {}\n"
        _write_if_changed(main_go, text)

    placeholder_import = "github.com/GIT_USER_ID/GIT_REPO_ID/encypher"
    test_dir = output_dir / "test"
    if test_dir.exists():
        for test_file in test_dir.rglob("*.go"):
            text = test_file.read_text(encoding="utf-8")
            text = text.replace(placeholder_import, GO_MODULE_PATH)
            text = re.sub(r"(?m)^package\s+encypher\s*$", "package encypher_test", text)
            _write_if_changed(test_file, text)

    docs_dir = output_dir / "docs"
    if docs_dir.exists():
        for doc_file in docs_dir.rglob("*.md"):
            text = doc_file.read_text(encoding="utf-8")
            text = text.replace(placeholder_import, GO_MODULE_PATH)
            _write_if_changed(doc_file, text)


def _patch_rust_metadata(output_dir: Path) -> None:
    cargo_toml = output_dir / "Cargo.toml"
    if not cargo_toml.exists():
        return
    text = cargo_toml.read_text(encoding="utf-8")

    package_block = re.search(r"(?ms)(^\[package\]\s*\n)(.*?)(^\[|\Z)", text)
    if package_block:
        header, body, tail = package_block.group(1), package_block.group(2), package_block.group(3)

        def upsert_package_field(key: str, value: str) -> None:
            nonlocal body
            if re.search(rf"(?m)^{re.escape(key)}\s*=\s*\".*\"\s*$", body):
                body = re.sub(
                    rf"(?m)^{re.escape(key)}\s*=\s*\".*\"\s*$",
                    f'{key} = "{value}"',
                    body,
                )
            else:
                if body and not body.endswith("\n"):
                    body += "\n"
                body += f'{key} = "{value}"\n'

        def upsert_package_array(key: str, value: str) -> None:
            nonlocal body
            if re.search(rf"(?m)^{re.escape(key)}\s*=\s*\[.*\]\s*$", body):
                body = re.sub(
                    rf"(?m)^{re.escape(key)}\s*=\s*\[.*\]\s*$",
                    f"{key} = [{value}]",
                    body,
                )
            else:
                if body and not body.endswith("\n"):
                    body += "\n"
                body += f"{key} = [{value}]\n"

        upsert_package_field("homepage", HOMEPAGE_URL)
        upsert_package_field("repository", MONOREPO_URL)
        upsert_package_field("documentation", f"{PRODUCTION_BASE_URL}/docs")
        upsert_package_field("license", "MIT")
        upsert_package_array("authors", '"Encypher <sdk@encypherai.com>"')

        text = text[: package_block.start(1)] + header + body + tail + text[package_block.end(3) :]

    _write_if_changed(cargo_toml, text)

    config_rs = output_dir / "src" / "apis" / "configuration.rs"
    if config_rs.exists():
        text = config_rs.read_text(encoding="utf-8")
        text = text.replace('base_path: "http://localhost".to_owned(),', f'base_path: "{PRODUCTION_BASE_URL}".to_owned(),')
        _write_if_changed(config_rs, text)


def run_cmd(cmd: list, capture: bool = True, stream_output: bool = False) -> subprocess.CompletedProcess:
    """Run a command, handling Windows shell requirements.
    
    Note: shell=True is required on Windows for npx to work correctly.
    The commands are constructed internally, not from user input.
    """
    if IS_WINDOWS:  # noqa: S602
        # Join command for shell execution on Windows
        cmd_str = " ".join(f'"{c}"' if " " in c else c for c in cmd)
        
        if stream_output:
            # For streaming, run and capture but print as we go
            process = subprocess.Popen(  # noqa: S602
                cmd_str,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate()
            
            # Print output lines
            for line in stdout.split("\n"):
                if line.strip():
                    if RICH_AVAILABLE:
                        console.print(f"  [dim]{line}[/dim]")
                    else:
                        print(f"  {line}")
            
            return subprocess.CompletedProcess(
                cmd_str, process.returncode, stdout, stderr
            )
        
        return subprocess.run(  # noqa: S602
            cmd_str,
            shell=True,
            capture_output=capture,
            text=True,
        )
    
    if stream_output:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        
        for line in stdout.split("\n"):
            if line.strip():
                if RICH_AVAILABLE:
                    console.print(f"  [dim]{line}[/dim]")
                else:
                    print(f"  {line}")
        
        return subprocess.CompletedProcess(
            cmd, process.returncode, stdout, stderr
        )
    
    return subprocess.run(cmd, capture_output=capture, text=True)


def check_openapi_generator() -> Optional[str]:
    """Check if openapi-generator-cli is installed. Returns version or None."""
    log_info("Checking openapi-generator-cli...")
    result = run_cmd(["npx", "--yes", "@openapitools/openapi-generator-cli", "version"])
    if result.returncode != 0:
        log_error("openapi-generator-cli not found")
        log_info("Install with: npm install -g @openapitools/openapi-generator-cli")
        log_info("Or use npx (will download on first use)")
        return None
    version = result.stdout.strip().split("\n")[-1]  # Get last line (version)
    log_success(f"openapi-generator-cli v{version}")
    return version


def get_api_info() -> dict:
    """Get API info from OpenAPI spec."""
    with open(OPENAPI_SPEC) as f:
        spec = json.load(f)
    return {
        "version": spec.get("info", {}).get("version", "0.0.0"),
        "title": spec.get("info", {}).get("title", "Unknown"),
        "endpoints": len(spec.get("paths", {})),
        "schemas": len(spec.get("components", {}).get("schemas", {})),
    }


def convert_version(api_version: str, format: str) -> str:
    """Convert API version to language-specific format."""
    if format == "pep440":
        # Python PEP 440: 1.0.0-preview -> 1.0.0a1
        if "-preview" in api_version:
            return api_version.replace("-preview", "a1")
        elif "-alpha" in api_version:
            return api_version.replace("-alpha", "a1")
        elif "-beta" in api_version:
            return api_version.replace("-beta", "b1")
        return api_version
    elif format == "npm":
        # npm: 1.0.0-preview -> 1.0.0-alpha.1
        if "-preview" in api_version:
            return api_version.replace("-preview", "-alpha.1")
        return api_version
    elif format == "semver":
        # Go/Rust semver: 1.0.0-preview -> 1.0.0-alpha.1
        if "-preview" in api_version:
            return api_version.replace("-preview", "-alpha.1")
        return api_version
    return api_version


def generate_sdk(language: str, api_info: dict, verbose: bool = False) -> bool:
    """Generate SDK for a specific language."""
    config = SDK_CONFIGS.get(language)
    if not config:
        log_error(f"Unknown language: {language}")
        return False
    
    output_dir = SDK_DIR / config["output_dir"]
    emoji = config["emoji"]
    name = config["name"]
    
    # Determine version format
    if language == "python":
        version = convert_version(api_info["version"], "pep440")
    elif language == "typescript":
        version = convert_version(api_info["version"], "npm")
    else:
        version = convert_version(api_info["version"], "semver")
    
    if RICH_AVAILABLE:
        console.print(f"\n{emoji} [bold]{name} SDK[/bold] (v{version})")
    else:
        print(f"\n{emoji} {name} SDK (v{version})")
    
    # Clean output directory
    if output_dir.exists():
        log_info(f"Cleaning {output_dir}...")
        shutil.rmtree(output_dir)
    
    # Build additional properties string
    props = config["additional_properties"].copy()
    if language == "python":
        props["packageVersion"] = version
    elif language == "typescript":
        props["npmVersion"] = version
    else:
        props["packageVersion"] = version
    
    props_str = ",".join(f"{k}={v}" for k, v in props.items())
    
    # Use forward slashes for paths (works on all platforms including Windows)
    spec_path = str(OPENAPI_SPEC).replace("\\", "/")
    out_path = str(output_dir).replace("\\", "/")
    
    cmd = [
        "npx", "--yes", "@openapitools/openapi-generator-cli", "generate",
        "-i", spec_path,
        "-g", config["generator"],
        "-o", out_path,
        "--additional-properties", props_str,
    ]
    
    log_info(f"Running openapi-generator ({config['generator']})...")
    
    start_time = time.time()
    result = run_cmd(cmd, stream_output=verbose)
    elapsed = time.time() - start_time
    
    if result.returncode != 0:
        log_error(f"{name} SDK generation failed!")
        if result.stderr:
            if RICH_AVAILABLE:
                console.print(Panel(result.stderr, title="Error Output", border_style="red"))
            else:
                print(f"Error: {result.stderr}")
        return False
    
    log_success(f"{name} SDK generated in {elapsed:.1f}s")
    log_info(f"Output: {output_dir}")
    
    # Create language-specific wrappers
    if language == "python":
        create_python_wrapper(output_dir)
        _patch_python_metadata(output_dir)
    elif language == "typescript":
        create_typescript_wrapper(output_dir)
        _patch_typescript_metadata(output_dir)
    elif language == "go":
        create_go_wrapper(output_dir)
        _patch_go_metadata(output_dir)
    elif language == "rust":
        create_rust_wrapper(output_dir)
        _patch_rust_metadata(output_dir)
    
    return True


def create_python_wrapper(output_dir: Path):
    """Create ergonomic wrapper for the generated Python SDK."""
    wrapper_content = '''"""
Encypher SDK - Python client for the Encypher Enterprise API.

This is an auto-generated SDK. For the source, see:
https://github.com/encypherai/encypherai-commercial/tree/main/sdk

Usage:
    from encypher.client import EncypherClient
    
    client = EncypherClient(api_key="your_api_key")
    result = client.sign(text="Hello, world!")
    print(result.signed_text)
"""

__all__ = [
    "EncypherClient",
]


class EncypherClient:
    """
    High-level client for the Encypher Enterprise API.
    
    This wraps the auto-generated API clients with a more ergonomic interface.
    
    Example:
        >>> client = EncypherClient(api_key="ency_...")
        >>> result = client.sign("Content to sign")
        >>> print(result.signed_text)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.encypherai.com",
    ):
        """
        Initialize the Encypher client.
        
        Args:
            api_key: Your Encypher API key
            base_url: API base URL (default: production)
        """
        from encypher.api_client import ApiClient
        from encypher.configuration import Configuration
        from encypher.api.signing_api import SigningApi
        from encypher.api.verification_api import VerificationApi
        
        self.config = Configuration(
            host=base_url,
            access_token=api_key,
        )
        self.api_client = ApiClient(self.config)
        
        # Initialize API instances
        self._signing = SigningApi(self.api_client)
        self._verification = VerificationApi(self.api_client)
    
    def sign(self, text: str, **kwargs):
        """Sign content with C2PA manifest."""
        from encypher.models import SignRequest
        request = SignRequest(text=text, **kwargs)
        return self._signing.sign_content_api_v1_sign_post(request)
    
    def verify(self, text: str):
        """Verify signed content."""
        from encypher.models import VerifyRequest
        request = VerifyRequest(text=text)
        return self._verification.verify_content_api_v1_verify_post(request)
    
    def close(self):
        """Close the client."""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
'''
    
    wrapper_path = output_dir / "encypher" / "client.py"
    wrapper_path.parent.mkdir(parents=True, exist_ok=True)
    wrapper_path.write_text(wrapper_content)
    log_info(f"Created wrapper: {wrapper_path.name}")


def create_typescript_wrapper(output_dir: Path):
    """Create ergonomic wrapper for the generated TypeScript SDK."""
    wrapper_content = '''/**
 * Encypher SDK - TypeScript client for the Encypher Enterprise API.
 * 
 * This is an auto-generated SDK. For the source, see:
 * https://github.com/encypherai/encypherai-commercial/tree/main/sdk
 * 
 * @example
 * ```typescript
 * import { EncypherClient } from '@encypher/sdk';
 * 
 * const client = new EncypherClient({ apiKey: 'your_api_key' });
 * const result = await client.sign({ text: 'Hello, world!' });
 * console.log(result.signedText);
 * ```
 */

import { Configuration, SigningApi, VerificationApi } from './apis';
import type { SignRequest, VerifyRequest } from './models';

export interface EncypherClientOptions {
  apiKey: string;
  baseUrl?: string;
}

export class EncypherClient {
  private config: Configuration;
  private signing: SigningApi;
  private verification: VerificationApi;

  constructor(options: EncypherClientOptions) {
    this.config = new Configuration({
      basePath: options.baseUrl || 'https://api.encypherai.com',
      accessToken: options.apiKey,
    });

    this.signing = new SigningApi(this.config);
    this.verification = new VerificationApi(this.config);
  }

  async sign(request: SignRequest) {
    return this.signing.signContentApiV1SignPost({ signRequest: request });
  }

  async verify(request: VerifyRequest) {
    return this.verification.verifyContentApiV1VerifyPost({ verifyRequest: request });
  }
}

// Re-export everything
export * from './apis';
export * from './models';
export * from './runtime';
'''
    
    wrapper_path = output_dir / "src" / "client.ts"
    wrapper_path.parent.mkdir(parents=True, exist_ok=True)
    wrapper_path.write_text(wrapper_content)
    log_info(f"Created wrapper: {wrapper_path.name}")


def create_go_wrapper(output_dir: Path):
    """Create ergonomic wrapper for the generated Go SDK."""
    wrapper_content = '''// Package encypher provides a client for the Encypher Enterprise API.
//
// This is an auto-generated SDK. For the source, see:
// https://github.com/encypherai/encypherai-commercial/tree/main/sdk
//
// Usage:
//
//	client := encypher.NewClient("your_api_key")
//	result, err := client.Sign(ctx, "Hello, world!")
//	if err != nil {
//	    log.Fatal(err)
//	}
//	fmt.Println(result.SignedText)
package encypher

import (
	"context"
)

// Client is a high-level client for the Encypher Enterprise API.
type Client struct {
	apiKey  string
	baseURL string
	api     *APIClient
}

// NewClient creates a new Encypher client.
func NewClient(apiKey string) *Client {
	return NewClientWithURL(apiKey, "https://api.encypherai.com")
}

// NewClientWithURL creates a new Encypher client with a custom base URL.
func NewClientWithURL(apiKey, baseURL string) *Client {
	cfg := NewConfiguration()
	cfg.Servers = ServerConfigurations{{URL: baseURL}}
	cfg.AddDefaultHeader("Authorization", "Bearer "+apiKey)
	
	return &Client{
		apiKey:  apiKey,
		baseURL: baseURL,
		api:     NewAPIClient(cfg),
	}
}

// Sign signs content with a C2PA manifest.
func (c *Client) Sign(ctx context.Context, text string) (*SignResponse, error) {
	req := NewSignRequest(text)
	return c.api.SigningAPI.SignContentApiV1SignPost(ctx).SignRequest(*req).Execute()
}

// Verify verifies signed content.
func (c *Client) Verify(ctx context.Context, text string) (*VerifyResponse, error) {
	req := NewVerifyRequest(text)
	return c.api.VerificationAPI.VerifyContentApiV1VerifyPost(ctx).VerifyRequest(*req).Execute()
}
'''
    
    wrapper_path = output_dir / "client_wrapper.go"
    wrapper_path.parent.mkdir(parents=True, exist_ok=True)
    wrapper_path.write_text(wrapper_content)
    log_info(f"Created wrapper: {wrapper_path.name}")


def create_rust_wrapper(output_dir: Path):
    """Create ergonomic wrapper for the generated Rust SDK."""
    wrapper_content = '''//! Encypher SDK - Rust client for the Encypher Enterprise API.
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
'''
    
    wrapper_path = output_dir / "src" / "client.rs"
    wrapper_path.parent.mkdir(parents=True, exist_ok=True)
    wrapper_path.write_text(wrapper_content)
    log_info(f"Created wrapper: {wrapper_path.name}")


def show_summary(results: dict, api_info: dict):
    """Show generation summary."""
    if RICH_AVAILABLE:
        table = Table(title="SDK Generation Summary")
        table.add_column("Language", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Output")
        
        for lang, success in results.items():
            config = SDK_CONFIGS.get(lang, {})
            status = "[green]✓ Success[/green]" if success else "[red]✗ Failed[/red]"
            output = f"sdk/{config.get('output_dir', lang)}/"
            table.add_row(f"{config.get('emoji', '')} {config.get('name', lang)}", status, output)
        
        console.print()
        console.print(table)
        console.print()
        console.print(f"[dim]API: {api_info['title']} v{api_info['version']}[/dim]")
        console.print(f"[dim]Endpoints: {api_info['endpoints']} | Schemas: {api_info['schemas']}[/dim]")
    else:
        print("\n=== SDK Generation Summary ===")
        for lang, success in results.items():
            config = SDK_CONFIGS.get(lang, {})
            status = "✓ Success" if success else "✗ Failed"
            print(f"  {config.get('name', lang)}: {status}")
        print(f"\nAPI: {api_info['title']} v{api_info['version']}")
        print(f"Endpoints: {api_info['endpoints']} | Schemas: {api_info['schemas']}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate SDKs from OpenAPI spec",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python sdk/generate_sdk.py python
  uv run python sdk/generate_sdk.py typescript go rust
  uv run python sdk/generate_sdk.py all --verbose
        """,
    )
    parser.add_argument(
        "languages",
        nargs="+",
        choices=list(SDK_CONFIGS.keys()) + ["all"],
        help="SDKs to generate",
    )
    parser.add_argument(
        "--spec",
        choices=["public", "internal"],
        default="public",
        help="Which OpenAPI spec to generate from (default: public)",
    )
    parser.add_argument(
        "--openapi-path",
        default=None,
        help="Override OpenAPI spec path (advanced)",
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip openapi-generator-cli check",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output from generator",
    )
    
    args = parser.parse_args()

    global OPENAPI_SPEC
    if args.openapi_path:
        OPENAPI_SPEC = Path(args.openapi_path)
    elif args.spec == "internal":
        OPENAPI_SPEC = OPENAPI_INTERNAL_SPEC
    else:
        OPENAPI_SPEC = OPENAPI_PUBLIC_SPEC
    
    # Show header
    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold blue]Encypher SDK Generator[/bold blue]\n"
            "[dim]Auto-generate SDKs from OpenAPI specification[/dim]",
            border_style="blue",
        ))
    else:
        print("=" * 40)
        print("Encypher SDK Generator")
        print("=" * 40)
    
    # Check prerequisites
    if not OPENAPI_SPEC.exists():
        log_error(f"OpenAPI spec not found: {OPENAPI_SPEC}")
        log_info("Run: uv run python sdk/generate_openapi.py")
        sys.exit(1)
    
    # Load API info
    api_info = get_api_info()
    log_success(f"Loaded OpenAPI spec: {api_info['endpoints']} endpoints, {api_info['schemas']} schemas")
    
    if not args.skip_check:
        if not check_openapi_generator():
            sys.exit(1)
    
    # Determine targets
    if "all" in args.languages:
        targets = list(SDK_CONFIGS.keys())
    else:
        targets = args.languages
    
    # Generate SDKs
    results = {}
    for target in targets:
        try:
            results[target] = generate_sdk(target, api_info, verbose=args.verbose)
        except Exception as e:
            log_error(f"Exception generating {target} SDK: {e}")
            results[target] = False
    
    # Show summary
    show_summary(results, api_info)
    
    # Exit code
    if all(results.values()):
        log_success("All SDKs generated successfully!")
        sys.exit(0)
    else:
        failed = [k for k, v in results.items() if not v]
        log_error(f"Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
