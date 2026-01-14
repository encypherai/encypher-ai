
# FingerprintDetectResponse

Response after fingerprint detection.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`fingerprintDetected` | boolean
`matches` | [Array&lt;FingerprintMatch&gt;](FingerprintMatch.md)
`bestMatch` | [FingerprintMatch](FingerprintMatch.md)
`processingTimeMs` | number
`message` | string

## Example

```typescript
import type { FingerprintDetectResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "fingerprintDetected": null,
  "matches": null,
  "bestMatch": null,
  "processingTimeMs": null,
  "message": null,
} satisfies FingerprintDetectResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as FingerprintDetectResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


