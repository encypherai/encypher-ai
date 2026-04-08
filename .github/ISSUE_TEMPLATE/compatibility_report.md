---
name: Compatibility Report
about: Report issues with how EncypherAI metadata renders or behaves in specific external software or environments.
title: '[COMPATIBILITY] Brief description of rendering/behavior issue'
labels: compatibility, external-dependency, documentation, needs-triage
assignees: ''
---

**NOTE:** This template is for reporting issues related to how EncypherAI's output appears or behaves in *other software* (like word processors, terminals, browsers) due to rendering or font limitations. This is typically *not* a bug within EncypherAI itself but rather an external compatibility problem.

## Describe the Compatibility Issue
A clear and concise description of the problem observed in the external software.
*e.g., "Variation selectors render as visible diamonds in LibreOffice Writer 7.6."*

## Steps to Reproduce
Please provide detailed steps to reliably reproduce the behavior:
1. Environment Setup: [e.g., Open LibreOffice Writer 7.6 on Ubuntu 22.04, set font to Liberation Serif]
2. Action: [e.g., Paste the following EncypherAI-encoded text: "Text..."]
3. Observation: [e.g., Describe where the incorrect rendering appears]
4.

## Expected Behavior
A clear and concise description of what you expected to happen.
*e.g., "The pasted text should appear normally, with the embedded metadata characters being invisible."*

## Actual Behavior
A clear and concise description of what actually happened.
*e.g., "Visible diamond characters appear interspersed within the text, usually near whitespace or punctuation."*

## Environment Details
Please provide as much detail as possible about the environment where the issue occurs:
- **Operating System:** [e.g., Windows 11, macOS Sonoma 14.4, Ubuntu 22.04 LTS]
- **Application & Version:** [e.g., Microsoft Word 365 (Version 2404), LibreOffice 7.6.5, Windows Terminal 1.19]
- **Font & Version (if known):** [e.g., Liberation Serif, Times New Roman, Consolas]
- **EncypherAI Version Used (if generating text):** [e.g., 2.0.1]

## Screenshots / Logs
Please add screenshots demonstrating the rendering issue. Ensure no sensitive information is displayed.
*(You can drag and drop images directly into the GitHub issue editor.)*

## Additional Context / Workarounds
Add any other relevant context here.
- Does this happen consistently?
- Have you found any specific fonts or application settings that work correctly or make it worse?
- Is copy/paste functionality also affected (e.g., does copying from the affected app change the text)?
