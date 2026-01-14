
# FingerprintMatch

Details of a detected fingerprint match.

## Properties

Name | Type
------------ | -------------
`fingerprintId` | string
`documentId` | string
`organizationId` | string
`confidence` | number
`markersFound` | number
`markersExpected` | number
`markerPositions` | Array&lt;number&gt;
`createdAt` | Date

## Example

```typescript
import type { FingerprintMatch } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "fingerprintId": null,
  "documentId": null,
  "organizationId": null,
  "confidence": null,
  "markersFound": null,
  "markersExpected": null,
  "markerPositions": null,
  "createdAt": null,
} satisfies FingerprintMatch

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as FingerprintMatch
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


