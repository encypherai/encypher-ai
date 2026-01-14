
# FingerprintDetectRequest

Request to detect a fingerprint in text.  Detection uses score-based matching with confidence threshold to identify fingerprinted content even after modifications.

## Properties

Name | Type
------------ | -------------
`text` | string
`fingerprintKey` | string
`confidenceThreshold` | number
`returnPositions` | boolean

## Example

```typescript
import type { FingerprintDetectRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "text": null,
  "fingerprintKey": null,
  "confidenceThreshold": null,
  "returnPositions": null,
} satisfies FingerprintDetectRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as FingerprintDetectRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


