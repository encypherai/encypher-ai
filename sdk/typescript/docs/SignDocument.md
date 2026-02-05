
# SignDocument

A single document in a batch sign request.

## Properties

Name | Type
------------ | -------------
`text` | string
`documentId` | string
`documentTitle` | string
`documentUrl` | string
`metadata` | { [key: string]: any; }

## Example

```typescript
import type { SignDocument } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "text": null,
  "documentId": null,
  "documentTitle": null,
  "documentUrl": null,
  "metadata": null,
} satisfies SignDocument

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SignDocument
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


