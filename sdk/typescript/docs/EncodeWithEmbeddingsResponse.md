
# EncodeWithEmbeddingsResponse

Response from encoding document with embeddings.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`documentId` | string
`merkleTree` | [MerkleTreeInfo](MerkleTreeInfo.md)
`embeddings` | [Array&lt;EmbeddingInfo&gt;](EmbeddingInfo.md)
`embeddedContent` | string
`statistics` | { [key: string]: any; }
`metadata` | { [key: string]: any; }

## Example

```typescript
import type { EncodeWithEmbeddingsResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "documentId": null,
  "merkleTree": null,
  "embeddings": null,
  "embeddedContent": null,
  "statistics": null,
  "metadata": null,
} satisfies EncodeWithEmbeddingsResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EncodeWithEmbeddingsResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


