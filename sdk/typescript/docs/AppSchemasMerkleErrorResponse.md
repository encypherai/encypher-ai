
# AppSchemasMerkleErrorResponse

Standard error response schema.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`error` | string
`message` | string
`details` | { [key: string]: any; }

## Example

```typescript
import type { AppSchemasMerkleErrorResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "error": null,
  "message": null,
  "details": null,
} satisfies AppSchemasMerkleErrorResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AppSchemasMerkleErrorResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


