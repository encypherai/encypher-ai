
# VerifyEmbeddingResponse

Response from verifying an embedding.

## Properties

Name | Type
------------ | -------------
`valid` | boolean
`refId` | string
`verifiedAt` | Date
`content` | [ContentInfo](ContentInfo.md)
`document` | [DocumentInfo](DocumentInfo.md)
`merkleProof` | [MerkleProofInfo](MerkleProofInfo.md)
`c2pa` | [C2PAInfo](C2PAInfo.md)
`licensing` | [LicensingInfo](LicensingInfo.md)
`verificationUrl` | string
`error` | string

## Example

```typescript
import type { VerifyEmbeddingResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "valid": null,
  "refId": null,
  "verifiedAt": null,
  "content": null,
  "document": null,
  "merkleProof": null,
  "c2pa": null,
  "licensing": null,
  "verificationUrl": null,
  "error": null,
} satisfies VerifyEmbeddingResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerifyEmbeddingResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


