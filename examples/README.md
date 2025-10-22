# EncypherAI Commercial Examples

This directory contains examples demonstrating how to use the EncypherAI commercial tools and shared library.

## Contents

- `sample_with_metadata.txt`: A sample text file with a representation of what EncypherAI metadata might look like
- `run_audit_example.ps1`: PowerShell script to demonstrate running the audit_log_cli on the sample file
- `trusted_signers/`: Directory created by the example script to store trusted signer public keys

## Running the Examples

### Audit Log CLI Example

To run the audit log CLI example:

```powershell
# Navigate to the examples directory
cd examples

# Run the example script
.\run_audit_example.ps1
```

This script will:

1. Navigate to the audit_log_cli directory
2. Set up and activate a virtual environment if needed
3. Install dependencies using UV
4. Create a sample trusted signers directory
5. Run the audit_log_cli to scan the sample file
6. Display the generated report

## Using the Shared Commercial Library Directly

You can also use the shared commercial library directly in your Python code:

```python
from encypher_commercial_shared import EncypherAI, VerificationResult
from encypher_commercial_shared.utils import scan_directory, generate_report

# Initialize the EncypherAI high-level API
encypher = EncypherAI(verbose=True)

# Verify metadata from a file
result = encypher.verify_from_file("examples/sample_with_metadata.txt")
print(f"Verified: {result.verified}, Signer: {result.signer_id}")

# Scan a directory for files with embedded metadata
results = scan_directory("examples", encypher)

# Generate a CSV report
generate_report(results, "examples/scan_report.csv")
```

For more detailed examples, see the test files in the `shared_commercial_libs/tests/` and `audit_log_cli/tests/` directories.
