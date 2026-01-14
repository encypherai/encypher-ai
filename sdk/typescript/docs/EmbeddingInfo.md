
# EmbeddingInfo

Information about a single embedding.

## Properties

Name | Type
------------ | -------------
`leafIndex` | number
`text` | string
`refId` | string
`signature` | string
`embedding` | string
`verificationUrl` | string
`leafHash` | string

## Example

```typescript
import type { EmbeddingInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "leafIndex": null,
  "text": null,
  "refId": null,
  "signature": null,
  "embedding": null,
  "verificationUrl": null,
  "leafHash": null,
} satisfies EmbeddingInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EmbeddingInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


