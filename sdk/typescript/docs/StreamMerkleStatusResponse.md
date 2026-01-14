
# StreamMerkleStatusResponse

Response with streaming Merkle session status.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`sessionId` | string
`documentId` | string
`status` | string
`totalSegments` | number
`bufferCount` | number
`intermediateRoot` | string
`createdAt` | Date
`expiresAt` | Date
`lastActivity` | Date

## Example

```typescript
import type { StreamMerkleStatusResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "sessionId": null,
  "documentId": null,
  "status": null,
  "totalSegments": null,
  "bufferCount": null,
  "intermediateRoot": null,
  "createdAt": null,
  "expiresAt": null,
  "lastActivity": null,
} satisfies StreamMerkleStatusResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StreamMerkleStatusResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


