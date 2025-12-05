
# APIKeyListResponse

Response schema for listing API keys.

## Properties

Name | Type
------------ | -------------
`keys` | Array&lt;{ [key: string]: any; }&gt;
`total` | number

## Example

```typescript
import type { APIKeyListResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "keys": null,
  "total": null,
} satisfies APIKeyListResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as APIKeyListResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


