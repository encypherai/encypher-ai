
# StreamMerkleSegmentRequest

Request to add a segment to an active streaming Merkle session.  Segments are buffered and combined into the Merkle tree incrementally. The tree is constructed using a bounded buffer approach for memory efficiency.

## Properties

Name | Type
------------ | -------------
`sessionId` | string
`segmentText` | string
`segmentIndex` | number
`isFinal` | boolean
`flushBuffer` | boolean

## Example

```typescript
import type { StreamMerkleSegmentRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "sessionId": null,
  "segmentText": null,
  "segmentIndex": null,
  "isFinal": null,
  "flushBuffer": null,
} satisfies StreamMerkleSegmentRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StreamMerkleSegmentRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


