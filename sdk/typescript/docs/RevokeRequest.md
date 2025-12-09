
# RevokeRequest

Request to revoke a document.

## Properties

Name | Type
------------ | -------------
`reason` | [RevocationReason](RevocationReason.md)
`reasonDetail` | string

## Example

```typescript
import type { RevokeRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "reason": null,
  "reasonDetail": null,
} satisfies RevokeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RevokeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


