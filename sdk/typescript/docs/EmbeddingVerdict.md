
# EmbeddingVerdict

Verification verdict for a single embedding.

## Properties

Name | Type
------------ | -------------
`index` | number
`valid` | boolean
`tampered` | boolean
`reasonCode` | string
`signerId` | string
`signerName` | string
`timestamp` | Date
`textSpan` | Array&lt;any&gt;
`cleanText` | string
`manifest` | { [key: string]: any; }

## Example

```typescript
import type { EmbeddingVerdict } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "index": null,
  "valid": null,
  "tampered": null,
  "reasonCode": null,
  "signerId": null,
  "signerName": null,
  "timestamp": null,
  "textSpan": null,
  "cleanText": null,
  "manifest": null,
} satisfies EmbeddingVerdict

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EmbeddingVerdict
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


