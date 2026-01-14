
# SourceRecord

A single source record in the lookup results.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`organizationId` | string
`organizationName` | string
`segmentHash` | string
`leafIndex` | number
`merkleRootHash` | string
`createdAt` | Date
`signedAt` | Date
`confidence` | number
`authorityScore` | number
`isOriginal` | boolean
`previousSourceId` | string
`nextSourceId` | string
`metadata` | { [key: string]: any; }

## Example

```typescript
import type { SourceRecord } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "organizationId": null,
  "organizationName": null,
  "segmentHash": null,
  "leafIndex": null,
  "merkleRootHash": null,
  "createdAt": null,
  "signedAt": null,
  "confidence": null,
  "authorityScore": null,
  "isOriginal": null,
  "previousSourceId": null,
  "nextSourceId": null,
  "metadata": null,
} satisfies SourceRecord

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SourceRecord
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


