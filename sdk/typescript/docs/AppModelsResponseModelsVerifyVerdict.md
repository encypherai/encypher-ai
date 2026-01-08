
# AppModelsResponseModelsVerifyVerdict

Detailed verification verdict data.

## Properties

Name | Type
------------ | -------------
`valid` | boolean
`tampered` | boolean
`reasonCode` | string
`signerId` | string
`signerName` | string
`timestamp` | Date
`details` | { [key: string]: any; }
`embeddingsFound` | number
`allEmbeddings` | [Array&lt;EmbeddingVerdict&gt;](EmbeddingVerdict.md)

## Example

```typescript
import type { AppModelsResponseModelsVerifyVerdict } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "valid": null,
  "tampered": null,
  "reasonCode": null,
  "signerId": null,
  "signerName": null,
  "timestamp": null,
  "details": null,
  "embeddingsFound": null,
  "allEmbeddings": null,
} satisfies AppModelsResponseModelsVerifyVerdict

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AppModelsResponseModelsVerifyVerdict
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


