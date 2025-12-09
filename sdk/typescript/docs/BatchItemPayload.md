
# BatchItemPayload

Single document payload within a batch request.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`text` | string
`title` | string
`metadata` | { [key: string]: any; }

## Example

```typescript
import type { BatchItemPayload } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "text": null,
  "title": null,
  "metadata": null,
} satisfies BatchItemPayload

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BatchItemPayload
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


