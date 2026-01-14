
# StreamMerkleStartRequest

Request to start a streaming Merkle tree construction session.  Patent Reference: FIG. 5 - Streaming Merkle Tree Construction  This initiates a session that allows segments to be added incrementally, ideal for real-time LLM output signing where content is generated token-by-token.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`segmentationLevel` | string
`metadata` | { [key: string]: any; }
`bufferSize` | number
`autoFinalizeTimeoutSeconds` | number

## Example

```typescript
import type { StreamMerkleStartRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "segmentationLevel": null,
  "metadata": null,
  "bufferSize": null,
  "autoFinalizeTimeoutSeconds": null,
} satisfies StreamMerkleStartRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StreamMerkleStartRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


