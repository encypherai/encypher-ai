
# BatchItemResult

Per-item response object emitted in batch responses.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`status` | string
`signedText` | string
`embeddedContent` | string
`verdict` | [AppModelsResponseModelsVerifyVerdict](AppModelsResponseModelsVerifyVerdict.md)
`errorCode` | string
`errorMessage` | string
`statistics` | { [key: string]: any; }

## Example

```typescript
import type { BatchItemResult } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "status": null,
  "signedText": null,
  "embeddedContent": null,
  "verdict": null,
  "errorCode": null,
  "errorMessage": null,
  "statistics": null,
} satisfies BatchItemResult

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BatchItemResult
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


