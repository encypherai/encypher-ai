
# DocumentStatusResponse

Response for document status query.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`organizationId` | string
`revoked` | boolean
`revokedAt` | string
`revokedReason` | string
`revokedReasonDetail` | string
`reinstatedAt` | string
`statusListUrl` | string
`statusListIndex` | number
`statusBitIndex` | number

## Example

```typescript
import type { DocumentStatusResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "organizationId": null,
  "revoked": null,
  "revokedAt": null,
  "revokedReason": null,
  "revokedReasonDetail": null,
  "reinstatedAt": null,
  "statusListUrl": null,
  "statusListIndex": null,
  "statusBitIndex": null,
} satisfies DocumentStatusResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as DocumentStatusResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


