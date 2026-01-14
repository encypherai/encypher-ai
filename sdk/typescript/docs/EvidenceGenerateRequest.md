
# EvidenceGenerateRequest

Request to generate an evidence package for content attribution.  Patent Reference: FIG. 11 - Evidence Generation & Attribution Flow

## Properties

Name | Type
------------ | -------------
`targetText` | string
`documentId` | string
`includeMerkleProof` | boolean
`includeSignatureChain` | boolean
`includeTimestampProof` | boolean
`exportFormat` | string

## Example

```typescript
import type { EvidenceGenerateRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "targetText": null,
  "documentId": null,
  "includeMerkleProof": null,
  "includeSignatureChain": null,
  "includeTimestampProof": null,
  "exportFormat": null,
} satisfies EvidenceGenerateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EvidenceGenerateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


