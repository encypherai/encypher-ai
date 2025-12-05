
# RevocationResponse

Response for revocation/reinstatement actions.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`documentId` | string
`action` | string
`timestamp` | string
`message` | string

## Example

```typescript
import type { RevocationResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "documentId": null,
  "action": null,
  "timestamp": null,
  "message": null,
} satisfies RevocationResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RevocationResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


