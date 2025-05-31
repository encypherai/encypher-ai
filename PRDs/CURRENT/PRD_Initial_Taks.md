**Product Requirements Document: EncypherAI - Commercial AI Governance Features (Phase 1)**

**1. Introduction / Overview**

* **1.1 Purpose:** This document outlines the initial set of commercial features to be developed for the EncypherAI platform. These features are designed to be implementable swiftly and will form the core of an "AI Governance Solution" that our System Integration (SI) partners, starting with Baleen Data, can offer to enterprise clients.
* **1.2 Target Users (via SI Partners):**
    * Enterprise Compliance Officers (like "David" from our ICPs)[cite: 1052].
    * AI Governance Teams & Legal Departments within enterprises.
    * AI Security & Data Governance Consultants (like "Susan" from our ICPs) [cite: 1026] who will use these tools as part of their service delivery.
* **1.3 Goals:**
    * Provide tangible, high-value tools that address enterprise needs for AI content auditability, compliance, and internal governance[cite: 496, 497].
    * Enable SI partners like Baleen Data to offer a compelling, differentiated AI Governance Solution built around EncypherAI.
    * Generate early commercial proof points by delivering features that enterprises are willing to pay for as part of a commercial license.
    * Ensure these initial features can be developed and deployed relatively quickly, leveraging our existing core metadata embedding and verification technology.

** USE uv TO MANAGE PYTHON DEPENDENCIES IN THIS REPO**

**2. Features**

**2.1 Feature: Basic Audit Log & Report Generation Utility**

* **2.1.1 Goal:** To provide enterprises with the ability to generate auditable reports on AI-generated content that has been processed with EncypherAI metadata, supporting compliance and internal oversight.
* **2.1.2 User Stories:**
    * "As David (CCO), I want to generate a quarterly report of AI model usage across departments so that I can demonstrate compliance with internal AI policies and external regulations like the EU AI Act."
    * "As Susan (AI Security Consultant), I want to provide my clients with a verifiable log of their AI-generated content, showing provenance and signature status, as part of my AI governance implementation service."
* **2.1.3 Requirements / Scope (V1):**
    * Command-Line Interface (CLI) tool primarily, for speed of development.
    * Ability to scan a specified directory of text files or accept a list of text inputs.
    * Parses EncypherAI metadata from compliant texts.
    * Outputs a report (initially CSV format) containing:
        * Filename/Identifier
        * Signature Status (Valid, Invalid, Missing)
        * Timestamp of generation (from metadata)
        * Model ID (from metadata)
        * Key ID used for signing (from metadata)
        * Any specified custom metadata fields (e.g., `department_id`, `project_code`).
    * Basic error handling for non-compliant files or unreadable metadata.
* **2.1.4 Tasks & Subtasks:**
    * `[ ]` **0. Project Setup (in `encypherai-commercial/audit_log_cli/`)**
        * `[ ]` 0.1. Initialize Python package structure (e.g., `audit_log_cli/app/`).
        * `[ ]` 0.2. Ensure `encypher-ai` (OS package) is a dependency and importable.
        * `[ ]` 0.3. Set up basic CLI entry point (e.g., using `argparse` or `typer` in `app/main.py`).
    * `[ ]` **1. Backend Logic Development (within `audit_log_cli/app/`)**
        * `[ ]` 1.1. Develop file/input scanning module.
            * `[ ]` 1.1.1. Implement directory traversal for text files.
            * `[ ]` 1.1.2. Implement handling for list of text string inputs.
        * `[ ]` 1.2. **Utilize** core `encypher-ai` library for metadata extraction & verification.
        * `[ ]` 1.3. Develop logic to aggregate extracted metadata for reporting.
        * `[ ]` 1.4. Implement error handling for parsing and verification failures.
    * `[ ]` **2. Report Generation (within `audit_log_cli/app/`)**
        * `[ ]` 2.1. Design CSV report format (define columns).
        * `[ ]` 2.2. Implement CSV export functionality.
    * `[ ]` **3. CLI Interface (refining `app/main.py`)**
        * `[ ]` 3.1. Define CLI arguments (input path/list, output file, optional custom fields to include).
        * `[ ]` 3.2. Implement CLI command structure.
        * `[ ]` 3.3. Add basic progress indicators (e.g., using `rich.progress`).
    * `[ ]` **4. Documentation & Testing (within `audit_log_cli/`)**
        * `[ ]` 4.1. Write unit tests for backend logic and CLI commands.
        * `[ ]` 4.2. Conduct integration testing with various sample data.
        * `[ ]` 4.3. Create user documentation for installing and using this commercial CLI tool.

**2.2 Feature: Metadata Policy Validation Tool**

* **2.2.1 Goal:** To enable enterprises to define and enforce internal policies regarding the content and structure of EncypherAI metadata, ensuring consistency and adherence to governance standards.
* **2.2.2 User Stories:**
    * "As David (CCO), I want to ensure all AI-generated legal documents include a `case_id` and `sensitivity_level` in their EncypherAI metadata, so we can track usage and apply appropriate controls."
    * "As Susan (Consultant), I want to help my clients set up metadata policies and then run validation checks to demonstrate the effectiveness of the new governance framework."
* **2.2.3 Requirements / Scope (V1):**
    * CLI tool primarily.
    * Ability to define a simple metadata policy schema (e.g., via a JSON configuration file).
        * Schema should specify required metadata keys.
        * Schema can optionally specify expected data types (string, integer, boolean) for values (basic validation).
        * Schema can optionally specify allowed values for certain keys (enum-like).
    * Scans input texts (directory or list) containing EncypherAI metadata.
    * Compares extracted metadata against the defined policy schema.
    * Outputs a report (CSV initially) highlighting:
        * Compliant metadata instances.
        * Non-compliant instances, with details of the policy violation (e.g., missing key, incorrect data type, unallowed value).
* **2.2.4 Tasks & Subtasks:**
    * `[ ]` **0. Project Setup (in `encypherai-commercial/policy_validator_cli/`)**
        * `[ ]` 0.1. Initialize Python package structure (e.g., `policy_validator_cli/app/`).
        * `[ ]` 0.2. Ensure `encypher-ai` (OS package) is a dependency and importable.
        * `[ ]` 0.3. Set up basic CLI entry point (e.g., `app/main.py`).
    * `[ ]` **1. Policy Schema Definition & Parsing (within `policy_validator_cli/app/`)**
        * `[ ]` 1.1. Design the structure for the JSON policy configuration file.
        * `[ ]` 1.2. Develop a module to load and parse the policy schema.
    * `[ ]` **2. Backend Validation Logic (within `policy_validator_cli/app/`)**
        * `[ ]` 2.1. **Utilize** core `encypher-ai` library for metadata extraction.
        * `[ ]` 2.2. Develop logic to compare extracted metadata against the parsed policy schema.
            * `[ ]` 2.2.1. Implement check for required keys.
            * `[ ]` 2.2.2. Implement basic data type validation.
            * `[ ]` 2.2.3. Implement check for allowed values.
        * `[ ]` 2.3. Aggregate validation results (pass/fail + reasons for failure).
    * `[ ]` **3. Report Generation (within `policy_validator_cli/app/`)**
        * `[ ]` 3.1. Design CSV report format for validation results.
        * `[ ]` 3.2. Implement CSV export functionality.
    * `[ ]` **4. CLI Interface (refining `app/main.py`)**
        * `[ ]` 4.1. Define CLI arguments (input path/list, policy file path, output file).
        * `[ ]` 4.2. Implement CLI command structure.
    * `[ ]` **5. Documentation & Testing (within `policy_validator_cli/`)**
        * `[ ]` 5.1. Write unit tests for validation logic and CLI.
        * `[ ]` 5.2. Test with various policy schemas and data sets.
        * `[ ]` 5.3. Create user documentation for this commercial CLI tool.

**3. "Compliance Readiness" Dashboard - Design Principles & Description (V1)**

* **3.1 General Design Philosophy:** The dashboard will embody EncypherAI's brand personality: **Trustworthy, Transparent & Open, Developer-Friendly (for admins), Confident yet Accessible.** It must be clean, modern, and provide clear, actionable insights without overwhelming the user.
* **3.2 Visual Identity Alignment (from Marketing Guidelines):**
    * **Color Palette:** Primarily Deep Navy (`#1B2F50`) for backgrounds/major elements, Azure Blue (`#2A87C4`) for primary actions/highlights, Light Sky Blue (`#B7D5ED`) for secondary elements, and Neutral Gray (`#A7AFBC`) for text, with White (`#FFFFFF`) for core content areas. Soft Rose Accent (`#BA8790`) to be used sparingly for critical alerts or notifications.
    * **Typography:** Clean, readable sans-serif fonts (e.g., Roboto, Open Sans) with clear hierarchy.
    * **Layout:** High-contrast, spacious, uncluttered. Use of cards or distinct sections for different metrics.
    * **Iconography:** Simple, geometric, and friendly icons (e.g., a shield for compliance, a checkmark for verified, an alert icon for issues).
* **3.3 Key Sections / Modules (V1 - assuming data is fed from the Audit & Policy tools):**
    * **1. Overview / Summary Stats:**
        * `[ ]` 1.1. Total documents/texts scanned within a selectable timeframe.
        * `[ ]` 1.2. Percentage of scanned content with **Valid** EncypherAI Signatures.
        * `[ ]` 1.3. Number of texts with **Invalid/Missing** Signatures (critical alert).
        * `[ ]` 1.4. Number of **Metadata Policy Violations** detected (critical alert).
        * `[ ]` 1.5. (Optional V1) Simple trend graph for "Valid Signatures" over time (e.g., last 30 days).
    * **2. Recent Activity / Alerts:**
        * `[ ]` 2.1. A chronological feed or list of recent significant events (e.g., "15 policy violations detected in 'Legal Department' scan," "Large batch of unsigned documents detected from 'Marketing AI Tool'").
        * `[ ]` 2.2. Prioritized alerts for critical issues.
    * **3. AI Model Usage Insights (Basic):**
        * `[ ]` 3.1. Simple bar chart or list showing the count of texts generated by different `model_id`s (top 5-10 models).
    * **4. Drill-Down / Reporting Links (Placeholder for V1):**
        * `[ ]` 4.1. Links to download the full CSV reports generated by the backend Audit Log and Policy Validation tools. (V1 dashboard is for visualization; full data export via existing tools).
* **3.4 Look and Feel:**
    * The dashboard should feel professional and give a sense of control and insight.
    * Data visualizations (charts) should be simple, clear, and easy to interpret.
    * Navigation (if multiple pages/views in future versions) should be intuitive.
    * Tooltips for explaining metrics or chart elements.
* **3.5 Tasks & Subtasks (Dashboard V1):**
    * `[ ]` **0. Project Setup (in `encypherai-commercial/dashboard_app/`)**
        * `[ ]` 0.1. Initialize backend project structure (FastAPI in `/backend/`).
            * `[ ]` 0.1.1. Ensure `encypher-ai` is a dependency for the backend.
        * `[ ]` 0.2. Initialize frontend project structure (Next.js in `/frontend/`).
        * `[ ]` 0.3. Define basic API contract between backend and frontend.
    * `[ ]` **1. Backend Data Aggregation & API (in `/dashboard_app/backend/`)**
        * `[ ]` 1.1. Develop API endpoints to serve aggregated data for dashboard views.
            * `[ ]` 1.1.1. This might involve the backend calling the Audit Log / Policy Validator CLI tools as subprocesses initially or directly using their library code if refactored for such use.
            * `[ ]` 1.1.2. Or, develop logic to periodically run these tools and store summary results in a simple database accessible by the dashboard backend.
        * `[ ]` 1.2. Implement secure authentication/authorization for API endpoints.
    * `[ ]` **2. Frontend Development (in `/dashboard_app/frontend/`)**
        * `[ ]` 2.1. Setup basic web application framework & routing.
        * `[ ]` 2.2. Develop UI components for each dashboard section (Overview, Recent Activity, Model Usage) as defined in PRD 3.3.
        * `[ ]` 2.3. Implement data visualization for charts (using a lightweight charting library).
        * `[ ]` 2.4. Ensure responsive design.
        * `[ ]` 2.5. Style according to EncypherAI visual guidelines.
        * `[ ]` 2.6. Implement user authentication flow (login page, session management).
    * `[ ]` **3. API/Data Integration**
        * `[ ]` 3.1. Connect frontend components to backend API endpoints.
    * `[ ]` **4. Deployment (Placeholder for V1 strategy)**
        * `[ ]` 4.1. Research and decide on initial hosting/deployment strategy for the dashboard web application.
    * `[ ]` **5. Testing & Documentation (within `dashboard_app/`)**
        * `[ ]` 5.1. Test dashboard with sample data and backend APIs.
        * `[ ]` 5.2. Basic user guide for accessing and interpreting the dashboard.

**4. Success Metrics (for these features)**

* Successful deployment and use of these tools in the 3-5 enterprise pilots conducted with Baleen Data.
* Positive feedback from Baleen Data regarding the ease of selling and implementing the "AI Governance Solution" with these tools.
* Ability of pilot customers to generate meaningful audit reports and identify policy non-compliance.
* Conversion of pilot customers to paid commercial licenses, citing these tools as a key value driver.

**5. Future Considerations (Out of Scope for Swift Phase 1)**

* More advanced, interactive reporting and data drill-down within the dashboard.
* Real-time alerting and notification system.
* Integration with enterprise GRC (Governance, Risk, Compliance) platforms.
* User role-based access control for the dashboard and tools.
* Automated policy *enforcement* actions (beyond just validation).