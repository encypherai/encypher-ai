
# DecodeToolResponse

Response model for decoding.

## Properties

Name | Type
------------ | -------------
`metadata` | { [key: string]: any; }
`verificationStatus` | string
`error` | string
`rawHiddenData` | [AppRoutersToolsVerifyVerdict](AppRoutersToolsVerifyVerdict.md)

## Example

```typescript
import type { DecodeToolResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "metadata": null,
  "verificationStatus": null,
  "error": null,
  "rawHiddenData": null,
} satisfies DecodeToolResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as DecodeToolResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


