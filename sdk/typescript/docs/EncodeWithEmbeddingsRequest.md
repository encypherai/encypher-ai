
# EncodeWithEmbeddingsRequest

Request to encode document with minimal signed embeddings.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`text` | string
`segmentationLevel` | string
`action` | string
`previousInstanceId` | string
`metadata` | { [key: string]: any; }
`c2paManifestUrl` | string
`c2paManifestHash` | string
`customAssertions` | Array&lt;{ [key: string]: any; }&gt;
`validateAssertions` | boolean
`digitalSourceType` | string
`license` | [LicenseInfo](LicenseInfo.md)
`embeddingOptions` | [EmbeddingOptions](EmbeddingOptions.md)
`expiresAt` | Date

## Example

```typescript
import type { EncodeWithEmbeddingsRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "text": null,
  "segmentationLevel": null,
  "action": null,
  "previousInstanceId": null,
  "metadata": null,
  "c2paManifestUrl": null,
  "c2paManifestHash": null,
  "customAssertions": null,
  "validateAssertions": null,
  "digitalSourceType": null,
  "license": null,
  "embeddingOptions": null,
  "expiresAt": null,
} satisfies EncodeWithEmbeddingsRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EncodeWithEmbeddingsRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


