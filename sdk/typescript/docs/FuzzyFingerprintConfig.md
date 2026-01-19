
# FuzzyFingerprintConfig

Configuration for fuzzy fingerprint indexing at encode time.

## Properties

Name | Type
------------ | -------------
`enabled` | boolean
`algorithm` | string
`levels` | Array&lt;string&gt;
`includeDocumentFingerprint` | boolean
`fingerprintBits` | number
`bucketBits` | number

## Example

```typescript
import type { FuzzyFingerprintConfig } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "enabled": null,
  "algorithm": null,
  "levels": null,
  "includeDocumentFingerprint": null,
  "fingerprintBits": null,
  "bucketBits": null,
} satisfies FuzzyFingerprintConfig

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as FuzzyFingerprintConfig
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


