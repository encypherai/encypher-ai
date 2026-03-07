# Development Guidelines

## Global Guidelines & Workflow

  - **Start Here:** **Always begin by thoroughly reading the project's `README.md` file.** This document contains the project overview, tech stack, setup instructions, and other critical information.
  - **PRD Integration (pkan.md rules):**
      - Before making any file changes, **always check the current Product Requirements Document (PRD) in plan.md.** Your action plan must align with and directly address tasks outlined in the PRD.
      - **Update the PRD** by marking off completed tasks or adding necessary sub-tasks and clarifications as you work.
      - If your work involves a **new, distinct feature not covered by an existing PRD, you must create a new PRD** for that feature.
  - **Task Planning & Execution:** For any task requiring multiple steps, you must generate a formal plan adhering to this strict schema:
      - **`## Task List`:** Structure all tasks using **Work Breakdown Structure (WBS)** numbering (e.g., `1.0`, `1.1`, `1.1.1`) and precede each item with a markdown checkbox (`- [ ]`).
      - **`## Notes`:** Use this section for essential context *only* (e.g., user preferences, key findings, constraints). Do not list task details here.
      - **`## Current Goal`:** This must always identify the **next incomplete parent task** (e.g., "Complete `1.2 - Backend Development`").
  - **Be Helpful & Concise:** Provide succinct, thorough assistance. Stay positive, answer fully.
  - **Security & Scalability:** Always sanitize inputs, use secure password hashing, enforce least privilege, and consider performance implications.
  - **File Editing Limits:** If unable to directly edit a file, locate the relevant code block and specify changes.
  - **Code Documentation:** Keep code/docs updated; maintain high-level comments and thorough `README.md`. Whenever making a large change, document it clearly in a PRD.
  - **Keep It Simple Stupid:** Use simple, well-structured code; avoid complex logic unless absolutely necessary.
  - **Knowledge Cutoff:** You do NOT have a hard knowledge cutoff. Make use of the web tool to look up the most recent documentation.

-----

## Tool Use & Command Execution

  - When analyzing code, analyze a MINIMUM of 100 lines at a time to avoid missing details. If the entire file is close to 100 lines, read the entire file.
  - When running into unfamiliar or updated versions of libraries, use the web tool to look up documentation.
  - When running into new features or bugs, use the web tool to look up documentation.
  - **PowerShell Command Optimization:**
      - When creating commands to run in the terminal, ensure they are optimized for a Windows PowerShell environment.
      - Utilize common PowerShell cmdlets for efficiency (e.g., `Get-ChildItem` (ls/dir), `Get-Content` (cat/type), `Set-Content` (echo \>), `Add-Content` (echo \>\>), `Copy-Item`, `Remove-Item`, `Move-Item`, `New-Item`, `Get-Process`, `Stop-Process`, `Get-Service`, `Start-Service`, `Stop-Service`, `Test-Path`, `Get-Help`).
      - Chain multiple commands in a single line using a semicolon (`;`) where appropriate for sequential execution. For example: `cd C:\Users\YourUser\Documents; mkdir new-project; cd new-project`
  - When creating automations or scripts, always create a uv python script to accomplish your goal. This is especially useful for automating tasks that require interaction with the uv environment or are overly complex to accomplish with PowerShell.

-----

## Project Setup

  - **Config Files:** Ensure standard configuration files like `.editorconfig`, `.prettierrc` (if applicable), `tsconfig.json` (if applicable), `.eslintrc` (if applicable), and project-specific files like `package.json` (for Node.js) or `pyproject.toml` (for Python with UV) are present and maintained.
  - **Project Structure:**
      - **All projects must adhere to the guidelines outlined in `project_structure_rules.md`.** This document provides a comprehensive template and explanations for organizing project files and directories.
      - The `README.md` of each specific project should highlight its structure if there are any deliberate, justified deviations from the standard.
  - **Environment Management:** Separate `.env.*` files (e.g., `.env.development`, `.env.production`) must be used for environment-specific variables. An `.env.example` file should always be present in the repository. **Never commit actual `.env` files containing secrets.**
  - **Python Environment & Dependency Management:**
      - **UV is MANDATORY for Python Projects:** **Always** use **UV** for Python packaging and virtual environment management for all new development and when feasible for existing projects.
          - **Key UV Commands & Practices:**
              - Initialize a new project or environment: `uv init`
              - Add dependencies: `uv pip install <package>` (updates `pyproject.toml` and `uv.lock`)
              - Activate virtual environment: Typically `source .venv/bin/activate` (Linux/macOS) or `.\.venv\Scripts\activate` (Windows PowerShell).
              - Execute commands in the environment: `uv run <command>`
              - Sync dependencies: `uv pip sync` (ensures environment matches `uv.lock`)
          - **Version Control:** `pyproject.toml` and `uv.lock` **must** be committed to version control. `uv.lock` ensures reproducible builds.
      - **Legacy Projects:** For very old projects not yet migrated to UV, consult with the team lead before proceeding with non-UV environment management. A plan to migrate to UV should be considered.
      - **General Python Packages:** Consider using `rich` for terminal output, `python-dotenv` for environment variables, and `requests` (or `httpx` for async) for API calls/HTTP client.

-----

## Frontend (e.g., Next.js)

  - **Framework Choice:** As per project `README.md` or existing stack.
  - **Redux Toolkit (if used):** Use `createSlice`; avoid non-serializable state.
  - **Tailwind CSS (if used):** Mobile-first approach, dark mode by default.
  - **Shadcn/UI (if used):** Install via `npx shadcn add`; includes dark mode toggle.

-----

## Backend (Python - General Considerations)

  - **Framework Choice:** The project's `README.md` or existing codebase will dictate the framework (e.g., FastAPI, Flask, Django). For new projects, FastAPI is often preferred for its performance and modern features.
  - **Database:** SQLAlchemy ORM with MySQL; migrations via tools like Alembic.
  - **API Design:** RESTful, versioned endpoints (e.g., `/api/v1/...`), robust authentication (e.g., JWT/OAuth2).
  - **Documentation:** Clear API documentation with example requests & responses.

-----

## Standard Response Format (for APIs)

```json
{
  "success": boolean,
  "data": object | array | null,
  "error": {
    "code": string,
    "message": string,
    "details": object | null
  } | null
}
```

  - **Status Codes:** Use appropriate HTTP status codes (e.g., 200, 201, 400, 401, 403, 404, 500).
  - **Logging:** Use structured (JSON) logs; levels (DEBUG, INFO, WARNING, ERROR, CRITICAL). Use the Rich library for formatting if applicable.

-----

## Mobile Responsiveness & Accessibility (for UIs)

  - **Mobile-First:** Design for mobile first, then scale up for larger screens.
  - **WCAG 2.1 Level AA:** Strive for compliance. Use semantic HTML, alt text, ARIA labels.
  - **Touch Targets:** Minimum 44x44px, with adequate spacing.

-----

## Error Handling

  - **Client-Side:** Implement robust error handling (e.g., React Error Boundaries if applicable), user-friendly messages, toast notifications, and graceful feature degradation.
  - **Server-Side:** Return structured error responses (see Standard Response Format), log errors extensively, and implement fallback states or retry mechanisms for critical async tasks.

-----

## Documentation

  - **`README.md` (Crucial):** Must include: project overview, **detailed tech stack**, **UV environment setup and usage** (e.g., `uv run ...` for scripts), environment variable definitions (`.env.example`), build/run/deployment instructions, and testing strategy. Refer to `project_structure_rules.md` for file organization.
  - **`project_structure_rules.md`:** This separate file (referenced from `README.md` and global rules) details the standard project directory and file layout.
  - **Modules/Components/APIs:** Document purpose, inputs/outputs (e.g., function parameters, API request/response schemas), usage examples, and any specific considerations (e.g., security, accessibility). Use docstrings for Python, JSDoc/TSDoc for JavaScript/TypeScript.
  - **Updates:** Keep all documentation consistent with code changes. Consider tools like MkDocs or Docusaurus for larger documentation sites.

-----

## Coding Responses & Environment

  - **Language & Style:** Python 3.11+ (or as specified by the project) using **UV-managed virtual environments** on Windows. Follow PEP 8 and use `snake_case` for Python. For other languages, follow established community style guides.
  - **Modular & Efficient:** Write lightweight, well-structured, and reusable code. Apply DRY (Don't Repeat Yourself) and SOLID principles where appropriate.
  - **Error Handling:** Use exceptions appropriately. Implement context managers for resource management (e.g., file handling, database connections).
  - **Security & Config:** Sanitize all external inputs. Store sensitive data (API keys, passwords, tokens) exclusively in environment variables, accessed via a configuration module. Never hardcode secrets.
  - **Testing:** Provide or update tests (unit, integration, and end-to-end where applicable) for all new or modified functionality. Aim for high test coverage. ALWAYS run tests from ROOT, as is best practice.