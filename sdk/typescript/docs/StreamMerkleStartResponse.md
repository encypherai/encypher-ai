
# StreamMerkleStartResponse

Response after starting a streaming Merkle session.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`sessionId` | string
`documentId` | string
`expiresAt` | Date
`bufferSize` | number
`message` | string

## Example

```typescript
import type { StreamMerkleStartResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "sessionId": null,
  "documentId": null,
  "expiresAt": null,
  "bufferSize": null,
  "message": null,
} satisfies StreamMerkleStartResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StreamMerkleStartResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


