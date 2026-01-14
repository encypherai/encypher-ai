
# BatchVerifyRequest

Batch verification request (shares schema for now).

## Properties

Name | Type
------------ | -------------
`mode` | string
`segmentationLevel` | string
`idempotencyKey` | string
`items` | [Array&lt;BatchItemPayload&gt;](BatchItemPayload.md)
`failFast` | boolean

## Example

```typescript
import type { BatchVerifyRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "mode": null,
  "segmentationLevel": null,
  "idempotencyKey": null,
  "items": null,
  "failFast": null,
} satisfies BatchVerifyRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BatchVerifyRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


