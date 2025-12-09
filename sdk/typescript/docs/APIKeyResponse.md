
# APIKeyResponse

Response schema for API key.

## Properties

Name | Type
------------ | -------------
`apiKey` | string
`keyId` | string
`organizationId` | string
`tier` | string
`createdAt` | Date
`expiresAt` | Date

## Example

```typescript
import type { APIKeyResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "apiKey": null,
  "keyId": null,
  "organizationId": null,
  "tier": null,
  "createdAt": null,
  "expiresAt": null,
} satisfies APIKeyResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as APIKeyResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


