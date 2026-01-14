
# EvidencePackage

Complete evidence package for content attribution.  This package contains all cryptographic proofs needed to verify content provenance in legal or compliance contexts.

## Properties

Name | Type
------------ | -------------
`evidenceId` | string
`generatedAt` | Date
`targetTextHash` | string
`targetTextPreview` | string
`attributionFound` | boolean
`attributionConfidence` | number
`sourceDocumentId` | string
`sourceOrganizationId` | string
`sourceOrganizationName` | string
`merkleRootHash` | string
`merkleProof` | [Array&lt;MerkleProofItem&gt;](MerkleProofItem.md)
`merkleProofValid` | boolean
`signatureVerification` | [SignatureVerification](SignatureVerification.md)
`contentMatches` | [Array&lt;ContentMatch&gt;](ContentMatch.md)
`originalTimestamp` | Date
`timestampVerified` | boolean
`jsonExportUrl` | string
`pdfExportUrl` | string
`metadata` | { [key: string]: any; }

## Example

```typescript
import type { EvidencePackage } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "evidenceId": null,
  "generatedAt": null,
  "targetTextHash": null,
  "targetTextPreview": null,
  "attributionFound": null,
  "attributionConfidence": null,
  "sourceDocumentId": null,
  "sourceOrganizationId": null,
  "sourceOrganizationName": null,
  "merkleRootHash": null,
  "merkleProof": null,
  "merkleProofValid": null,
  "signatureVerification": null,
  "contentMatches": null,
  "originalTimestamp": null,
  "timestampVerified": null,
  "jsonExportUrl": null,
  "pdfExportUrl": null,
  "metadata": null,
} satisfies EvidencePackage

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EvidencePackage
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


