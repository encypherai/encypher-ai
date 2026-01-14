
# FingerprintEncodeRequest

Request to encode a robust fingerprint into text.  Fingerprints use secret-seeded placement of invisible markers that survive text modifications like paraphrasing or truncation.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`text` | string
`fingerprintDensity` | number
`fingerprintKey` | string
`metadata` | { [key: string]: any; }

## Example

```typescript
import type { FingerprintEncodeRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "text": null,
  "fingerprintDensity": null,
  "fingerprintKey": null,
  "metadata": null,
} satisfies FingerprintEncodeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as FingerprintEncodeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


