
# ExtractAndVerifyResponse

Response from extracting and verifying invisible embedding.

## Properties

Name | Type
------------ | -------------
`valid` | boolean
`verifiedAt` | Date
`content` | [ContentInfo](ContentInfo.md)
`document` | [DocumentInfo](DocumentInfo.md)
`merkleProof` | [MerkleProofInfo](MerkleProofInfo.md)
`c2pa` | [C2PAInfo](C2PAInfo.md)
`licensing` | [LicensingInfo](LicensingInfo.md)
`metadata` | { [key: string]: any; }
`error` | string

## Example

```typescript
import type { ExtractAndVerifyResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "valid": null,
  "verifiedAt": null,
  "content": null,
  "document": null,
  "merkleProof": null,
  "c2pa": null,
  "licensing": null,
  "metadata": null,
  "error": null,
} satisfies ExtractAndVerifyResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ExtractAndVerifyResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


