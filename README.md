# EncypherAI Commercial Suite

## 1. Overview of EncypherAI (The Company/Project)

EncypherAI is dedicated to establishing trust and verifiable provenance for AI-generated content[cite: 1, 72]. Our mission is to provide the foundational tools and standards necessary for a transparent and trustworthy digital ecosystem, addressing the "AI Content Trust Crisis"[cite: 2, 596].

At the heart of our initiative is the open-source `encypher-ai` core library, which enables the embedding and verification of cryptographic metadata directly within text.

## 2. Purpose of This Repository (`encypherai-commercial`)

This repository, `encypherai-commercial`, houses the **proprietary source code** for EncypherAI's commercial software offerings. These tools are built upon our core open-source `encypher-ai` library and are designed to provide advanced features, analytics, and enterprise-grade solutions for AI governance, compliance, and enhanced value extraction from verifiable metadata.

**Important:** The code in this repository is proprietary, subject to EncypherAI's commercial licensing terms, and is **NOT open source**. It is intended for the internal EncypherAI development team building our commercial products.

## 3. The EncypherAI Open-Source Core (Recap)

Our public `encypher-ai` Python package (AGPLv3 licensed, available on PyPI and [GitHub](https://github.com/encypher-ai/encypher-ai) provides the foundational capabilities for AI content provenance. Its main features include:

* **Core Library (`encypher.core`):**
    * Embedding invisible, cryptographically signed (Ed25519) metadata into text using Unicode variation selectors.
    * Verifying the authenticity and integrity of this embedded metadata using public key cryptography.
    * Support for "basic" key-value payloads and C2PA-inspired "manifest" payloads.
* **Streaming Handler (`encypher.streaming`):**
    * Real-time metadata processing and embedding for streaming text outputs.
* **Key Management Utilities (`encypher.core.keys`):**
    * Generation, loading, and saving of Ed25519 key pairs.
* **Examples (`/examples` in the open-source repository):**
    * Demonstrations of CLI usage (`cli_example.py`), FastAPI integration (`fastapi_example.py`), LiteLLM integration (`litellm_integration.py`), Jupyter notebook demos (`encypher_demo.ipynb`), and key generation (`generate_keys.py`).

All commercial tools developed in *this* repository will leverage the public `encypher-ai` package as a core dependency.

## 4. Commercial Tools Being Developed Here

This repository is structured as a monorepo to house the following initial commercial tools, designed to support an enterprise "AI Governance Solution" often delivered via partners like Baleen Data:

* **Audit Log & Report Generation Utility (CLI)**
    * **Location:** `/audit_log_cli/`
    * **Purpose:** A command-line tool for enterprise users to scan text assets, validate EncypherAI metadata, and generate auditable reports on AI content provenance, signature status, and key metadata attributes (e.g., model ID, timestamp). Supports compliance and internal oversight.
* **Metadata Policy Validation Tool (CLI)**
    * **Location:** `/policy_validator_cli/`
    * **Purpose:** A command-line tool allowing enterprises to define custom metadata policies (e.g., required fields, data types) and validate embedded EncypherAI metadata against these policies, ensuring adherence to internal governance standards.
* **"Compliance Readiness" Dashboard (Web Application)**
    * **Location:** `/dashboard_app/` (with subdirectories like `/backend` and `/frontend`)
    * **Purpose:** A web-based dashboard providing enterprise compliance officers and AI governance teams with at-a-glance visibility into AI content authenticity, metadata policy compliance, and basic AI model usage insights based on EncypherAI data.

## 5. Development Setup & Key Dependencies

* This is a Python-based monorepo. Each tool/application within its respective directory (`/audit_log_cli`, `/policy_validator_cli`, `/dashboard_app`) will manage its own specific dependencies in addition to shared ones.
* The primary and most crucial external dependency for all tools herein is the **`encypher-ai`** package (from PyPI). Ensure your development environment has access to and installs the latest compatible version of this public package.
    ```bash
    # Example:
    # pip install encypher-ai
    ```
* Refer to the individual `README.md` files within each tool's directory for specific setup and development instructions.

## 6. Contribution / Development Guidelines (Internal)

* All code in this repository is proprietary and confidential.
* Follow standard company coding guidelines, version control practices (Gitflow/feature branches), and PR review processes.
* Ensure robust testing (unit, integration) for all commercial features.
* Documentation for commercial tools (user guides, API docs if applicable) should be developed alongside the features.

---

This README should provide a good starting point for any developer joining the commercial product team. Remember to update it as new tools are added or the structure evolves.
