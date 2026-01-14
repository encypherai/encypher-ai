
# FingerprintEncodeResponse

Response after encoding a fingerprint.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`documentId` | string
`fingerprintId` | string
`fingerprintedText` | string
`fingerprintKeyHash` | string
`markersEmbedded` | number
`processingTimeMs` | number
`message` | string

## Example

```typescript
import type { FingerprintEncodeResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "documentId": null,
  "fingerprintId": null,
  "fingerprintedText": null,
  "fingerprintKeyHash": null,
  "markersEmbedded": null,
  "processingTimeMs": null,
  "message": null,
} satisfies FingerprintEncodeResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as FingerprintEncodeResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


