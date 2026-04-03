---
name: warn-env-file
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: "\.env($|\.)"
---

Writing to a .env file. Before proceeding, verify:
- No secrets, API keys, or credentials are hardcoded as literal values
- The file is listed in .gitignore and will not be committed
- If this is a .env.example, all values are placeholders only
