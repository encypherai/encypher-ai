
# StreamSignRequest

Request payload for streaming signing run.

## Properties

Name | Type
------------ | -------------
`text` | string
`documentId` | string
`documentTitle` | string
`documentType` | string
`runId` | string

## Example

```typescript
import type { StreamSignRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "text": null,
  "documentId": null,
  "documentTitle": null,
  "documentType": null,
  "runId": null,
} satisfies StreamSignRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StreamSignRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


