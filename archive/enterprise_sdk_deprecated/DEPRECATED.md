# DEPRECATED - Enterprise SDK

**Status**: DEPRECATED as of December 2025

## Why Deprecated?

This hand-crafted SDK has been superseded by the auto-generated SDKs in `/sdk/`.

**Reason**: SDKs must stay 100% in sync with the API. Auto-generation from OpenAPI guarantees this.

## Migration Path

### For API Calls
Use the canonical SDK from `/sdk/python/`:
```bash
pip install encypher
```

```python
from encypher.client import EncypherClient
client = EncypherClient(api_key="ency_...")
```

### For High-Level Features
The following features from this SDK may be extracted into a separate `encypher-extras` package in the future:

- **Integrations**: LangChain, LiteLLM, LlamaIndex, OpenAI wrappers
- **Batch Operations**: RepositorySigner, FileMetadata
- **Reports**: ReportGenerator, verification badges
- **State Management**: StateManager, FileState
- **Metadata Providers**: Git, Frontmatter parsing
- **Analytics**: MetricsCollector, DashboardExporter

## Archive Date
December 19, 2025

## Questions?
Contact sdk@encypher.com
