
# BatchVerifyResponse

Response from batch verification.

## Properties

Name | Type
------------ | -------------
`results` | [Array&lt;BatchVerifyResult&gt;](BatchVerifyResult.md)
`total` | number
`validCount` | number
`invalidCount` | number

## Example

```typescript
import type { BatchVerifyResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "results": null,
  "total": null,
  "validCount": null,
  "invalidCount": null,
} satisfies BatchVerifyResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BatchVerifyResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


