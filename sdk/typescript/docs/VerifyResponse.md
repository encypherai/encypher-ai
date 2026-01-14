
# VerifyResponse


## Properties

Name | Type
------------ | -------------
`success` | boolean
`data` | [VerifyVerdict](VerifyVerdict.md)
`error` | [ErrorDetail](ErrorDetail.md)
`correlationId` | string

## Example

```typescript
import type { VerifyResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "data": null,
  "error": null,
  "correlationId": null,
} satisfies VerifyResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerifyResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


