
# StreamMerkleFinalizeResponse

Response after finalizing a streaming Merkle session.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`sessionId` | string
`documentId` | string
`rootHash` | string
`treeDepth` | number
`totalSegments` | number
`embeddedContent` | string
`instanceId` | string
`processingTimeMs` | number
`message` | string

## Example

```typescript
import type { StreamMerkleFinalizeResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "sessionId": null,
  "documentId": null,
  "rootHash": null,
  "treeDepth": null,
  "totalSegments": null,
  "embeddedContent": null,
  "instanceId": null,
  "processingTimeMs": null,
  "message": null,
} satisfies StreamMerkleFinalizeResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StreamMerkleFinalizeResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


