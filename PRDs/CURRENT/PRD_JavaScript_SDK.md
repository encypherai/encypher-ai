# PRD: JavaScript/TypeScript SDK for Enterprise API

**Status:** Not Started
**Priority:** P0 (Critical)
**Owner:** TBD
**Created:** November 11, 2025
**Target Completion:** November 25, 2025

---

## Executive Summary

Create a production-ready JavaScript/TypeScript SDK that mirrors the Python SDK functionality, with first-class support for Next.js, React, and modern web applications.

---

## 🎯 Objectives

1. **Feature Parity** - Match Python SDK capabilities
2. **TypeScript First** - Full type safety and IntelliSense
3. **Framework Support** - Next.js, React, Vue, vanilla JS
4. **Modern Standards** - ESM, tree-shaking, zero dependencies (where possible)
5. **Developer Experience** - Intuitive API, great documentation

---

## 📋 Requirements

### 1. Core SDK Implementation

#### Project Structure
```
@encypher/enterprise-sdk/
├── src/
│   ├── client.ts              # Main EncypherClient class
│   ├── types.ts               # TypeScript types
│   ├── errors.ts              # Custom error classes
│   ├── utils/
│   │   ├── http.ts            # HTTP client wrapper
│   │   ├── crypto.ts          # Crypto utilities
│   │   └── validation.ts      # Input validation
│   ├── methods/
│   │   ├── sign.ts            # Signing methods
│   │   ├── verify.ts          # Verification methods
│   │   ├── embeddings.ts      # Enhanced embeddings
│   │   ├── merkle.ts          # Merkle tree operations
│   │   └── batch.ts           # Batch operations
│   └── index.ts               # Public API exports
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── examples/
│   ├── nextjs/                # Next.js example
│   ├── react/                 # React example
│   ├── node/                  # Node.js example
│   └── browser/               # Browser example
├── docs/
│   ├── api/                   # API reference
│   ├── guides/                # Integration guides
│   └── examples/              # Code examples
├── package.json
├── tsconfig.json
├── vitest.config.ts
└── README.md
```

#### Client Class API

```typescript
import { EncypherClient } from '@encypher/enterprise-sdk';

// Initialize client
const client = new EncypherClient({
  apiKey: 'encypher_...',
  baseUrl: 'https://api.encypher.com', // optional
  timeout: 30000, // optional
});

// Basic signing
const result = await client.sign({
  text: 'Content to sign',
  documentId: 'doc-123',
});

// Enhanced embeddings
const embedded = await client.signWithEmbeddings({
  text: 'Content to sign',
  documentId: 'doc-123',
  segmentationLevel: 'sentence',
});

// Verification
const verification = await client.verify({
  text: 'Signed content...',
});

// Batch operations
const batchResults = await client.batchSign([
  { text: 'Content 1', documentId: 'doc-1' },
  { text: 'Content 2', documentId: 'doc-2' },
]);

// Merkle tree retrieval
const merkleTree = await client.getMerkleTree({
  rootId: 'merkle-root-123',
});

// Sentence verification
const sentenceResult = await client.verifySentence({
  text: 'Single sentence to verify',
  merkleProof: [...],
});
```

#### TypeScript Types

```typescript
// Request types
export interface SignRequest {
  text: string;
  documentId: string;
  metadata?: Record<string, any>;
}

export interface SignWithEmbeddingsRequest {
  text: string;
  documentId: string;
  segmentationLevel?: 'sentence' | 'paragraph' | 'document';
  customAssertions?: CustomAssertion[];
}

export interface VerifyRequest {
  text: string;
}

// Response types
export interface SignResponse {
  signedContent: string;
  documentId: string;
  signature: string;
  timestamp: string;
}

export interface EmbeddingsResponse {
  embeddedContent: string;
  merkleTree: MerkleTree;
  embeddings: Embedding[];
  statistics: Statistics;
}

export interface VerifyResponse {
  valid: boolean;
  signer: string;
  timestamp: string;
  tampered: boolean;
  metadata?: Record<string, any>;
}

// Data types
export interface MerkleTree {
  rootId: string;
  rootHash: string;
  depth: number;
  leafCount: number;
  nodes: MerkleNode[];
}

export interface Embedding {
  leafIndex: number;
  hash: string;
  text: string;
  metadata: Record<string, any>;
}

// Error types
export class EncypherError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'EncypherError';
  }
}

export class AuthenticationError extends EncypherError {}
export class ValidationError extends EncypherError {}
export class RateLimitError extends EncypherError {}
```

### 2. Next.js Integration

#### React Hooks

```typescript
// hooks/useEncypher.ts
import { useEncypher } from '@encypher/enterprise-sdk/react';

function MyComponent() {
  const { sign, verify, loading, error } = useEncypher({
    apiKey: process.env.NEXT_PUBLIC_ENCYPHER_API_KEY!,
  });

  const handleSign = async () => {
    const result = await sign({
      text: 'Content to sign',
      documentId: 'doc-123',
    });
    console.log(result);
  };

  return (
    <div>
      <button onClick={handleSign} disabled={loading}>
        Sign Content
      </button>
      {error && <p>Error: {error.message}</p>}
    </div>
  );
}
```

#### Server Components

```typescript
// app/api/sign/route.ts
import { EncypherClient } from '@encypher/enterprise-sdk';

export async function POST(request: Request) {
  const client = new EncypherClient({
    apiKey: process.env.ENCYPHER_API_KEY!,
  });

  const { text, documentId } = await request.json();

  const result = await client.sign({ text, documentId });

  return Response.json(result);
}
```

#### Middleware

```typescript
// middleware.ts
import { createEncypherMiddleware } from '@encypher/enterprise-sdk/nextjs';

export const middleware = createEncypherMiddleware({
  apiKey: process.env.ENCYPHER_API_KEY!,
  autoSign: true, // Auto-sign responses
  routes: ['/api/content/*'], // Routes to protect
});
```

### 3. Build Configuration

#### Package.json

```json
{
  "name": "@encypher/enterprise-sdk",
  "version": "1.0.0",
  "description": "Enterprise SDK for Encypher API",
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    },
    "./react": {
      "import": "./dist/react.mjs",
      "require": "./dist/react.cjs",
      "types": "./dist/react.d.ts"
    },
    "./nextjs": {
      "import": "./dist/nextjs.mjs",
      "require": "./dist/nextjs.cjs",
      "types": "./dist/nextjs.d.ts"
    }
  },
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "tsup",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src",
    "typecheck": "tsc --noEmit",
    "prepublishOnly": "npm run build && npm run test"
  },
  "dependencies": {},
  "devDependencies": {
    "@types/node": "^20.0.0",
    "tsup": "^8.0.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0",
    "eslint": "^8.55.0"
  },
  "peerDependencies": {
    "react": "^18.0.0",
    "next": "^14.0.0"
  },
  "peerDependenciesMeta": {
    "react": {
      "optional": true
    },
    "next": {
      "optional": true
    }
  }
}
```

#### tsup.config.ts

```typescript
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: {
    index: 'src/index.ts',
    react: 'src/react/index.ts',
    nextjs: 'src/nextjs/index.ts',
  },
  format: ['cjs', 'esm'],
  dts: true,
  splitting: false,
  sourcemap: true,
  clean: true,
  treeshake: true,
  minify: true,
});
```

### 4. Testing Requirements

#### Unit Tests (Vitest)

```typescript
// tests/unit/client.test.ts
import { describe, it, expect, vi } from 'vitest';
import { EncypherClient } from '../src/client';

describe('EncypherClient', () => {
  it('should initialize with API key', () => {
    const client = new EncypherClient({ apiKey: 'test-key' });
    expect(client).toBeDefined();
  });

  it('should sign content', async () => {
    const client = new EncypherClient({ apiKey: 'test-key' });
    const result = await client.sign({
      text: 'Test content',
      documentId: 'test-doc',
    });
    expect(result.signedContent).toBeDefined();
  });

  // ... more tests
});
```

#### Integration Tests

```typescript
// tests/integration/api.test.ts
import { describe, it, expect } from 'vitest';
import { EncypherClient } from '../src/client';

describe('API Integration', () => {
  const client = new EncypherClient({
    apiKey: process.env.ENCYPHER_API_KEY!,
    baseUrl: 'http://localhost:9000',
  });

  it('should sign and verify content', async () => {
    const signResult = await client.sign({
      text: 'Integration test content',
      documentId: 'integration-test',
    });

    const verifyResult = await client.verify({
      text: signResult.signedContent,
    });

    expect(verifyResult.valid).toBe(true);
  });
});
```

### 5. Documentation

#### README.md

```markdown
# @encypher/enterprise-sdk

Enterprise SDK for Encypher API - Sign and verify content with C2PA standards.

## Installation

```bash
npm install @encypher/enterprise-sdk
# or
yarn add @encypher/enterprise-sdk
# or
pnpm add @encypher/enterprise-sdk
```

## Quick Start

```typescript
import { EncypherClient } from '@encypher/enterprise-sdk';

const client = new EncypherClient({
  apiKey: 'your-api-key',
});

const result = await client.sign({
  text: 'Content to sign',
  documentId: 'doc-123',
});
```

## Features

- ✅ TypeScript first with full type safety
- ✅ Next.js and React integration
- ✅ Enhanced embeddings with Merkle trees
- ✅ Batch operations
- ✅ Streaming support
- ✅ Zero dependencies (core)

## Documentation

- [API Reference](./docs/api/README.md)
- [Next.js Guide](./docs/guides/nextjs.md)
- [React Guide](./docs/guides/react.md)
- [Examples](./examples/)
```

---

## 📦 Deliverables

### Week 1: Foundation
- [ ] Project setup with TypeScript, tsup, Vitest
- [ ] Core client class implementation
- [ ] Basic signing and verification methods
- [ ] TypeScript types and error classes
- [ ] Unit tests (50%+ coverage)

### Week 2: Advanced Features
- [ ] Enhanced embeddings support
- [ ] Merkle tree operations
- [ ] Batch operations
- [ ] Streaming support
- [ ] Integration tests

### Week 3: Framework Integration
- [ ] React hooks implementation
- [ ] Next.js middleware and helpers
- [ ] Server component support
- [ ] Edge runtime compatibility
- [ ] Framework-specific tests

### Week 4: Polish & Release
- [ ] Complete documentation
- [ ] Example projects (Next.js, React, Node.js)
- [ ] 90%+ test coverage
- [ ] NPM package published
- [ ] CDN build available

---

## 🎯 Success Criteria

- [ ] Feature parity with Python SDK
- [ ] 90%+ test coverage
- [ ] Full TypeScript support with IntelliSense
- [ ] Works in Node.js, browser, and Edge runtime
- [ ] Published to NPM with proper versioning
- [ ] Complete documentation with examples
- [ ] Zero critical vulnerabilities
- [ ] Bundle size < 50KB (gzipped)

---

## 📊 Technical Specifications

### Browser Support
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Node.js 18+

### Bundle Sizes (Target)
- Core: ~30KB (gzipped)
- React: +5KB
- Next.js: +8KB

### Performance Targets
- Sign operation: <100ms
- Verify operation: <50ms
- Batch (10 items): <500ms

---

**Last Updated:** November 11, 2025
**Next Review:** November 18, 2025
