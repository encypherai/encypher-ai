# Encypher Dashboard Example Files

This directory contains example files with Encypher metadata for testing and demonstration purposes.

## File Categories

- **Financial Reports**: Example financial reports with metadata signed by encypherai-official, compliance-dept
- **Research Documents**: Example research documents with metadata signed by research-team, encypherai-official
- **Compliance Documents**: Example compliance documents with metadata signed by compliance-dept
- **External Documents**: Example external documents with metadata signed by untrusted-source

## Metadata Status

- **Valid Files**: Files with valid metadata and signatures
- **Tampered Content**: Files where the content was modified after metadata was embedded
- **Tampered Metadata**: Files where the metadata was tampered with
- **No Metadata**: Files without any Encypher metadata

## Trusted Signers

- **Encypher Official** (`encypherai-official`): Public key at `keys/encypherai-official-public.pem`
- **Compliance Department** (`compliance-dept`): Public key at `keys/compliance-dept-public.pem`
- **Research Team** (`research-team`): Public key at `keys/research-team-public.pem`
- **Untrusted Source** (`untrusted-source`): Public key at `keys/untrusted-source-public.pem`

## Usage

These files can be used to test the Encypher verification tools and dashboard functionality.
You can use the audit-log-cli tool to scan these files:

```
uv run -- python -m app.main --target examples/files --trusted-signers examples/files/keys --output dashboard_example_report.csv
```

Generated on: 2025-06-03 13:24:23
