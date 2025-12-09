
# EncodeToolResponse

Response model for encoding.

## Properties

Name | Type
------------ | -------------
`encodedText` | string
`metadata` | { [key: string]: any; }
`error` | string

## Example

```typescript
import type { EncodeToolResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "encodedText": null,
  "metadata": null,
  "error": null,
} satisfies EncodeToolResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EncodeToolResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


