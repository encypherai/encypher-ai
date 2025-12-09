
# APIKeyRevokeRequest

Request schema for revoking an API key.

## Properties

Name | Type
------------ | -------------
`keyId` | string
`reason` | string

## Example

```typescript
import type { APIKeyRevokeRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "keyId": null,
  "reason": null,
} satisfies APIKeyRevokeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as APIKeyRevokeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


