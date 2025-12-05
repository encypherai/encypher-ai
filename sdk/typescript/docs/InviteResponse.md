
# InviteResponse

Response after sending an invite.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`inviteId` | string
`email` | string
`role` | string
`expiresAt` | string
`message` | string

## Example

```typescript
import type { InviteResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "inviteId": null,
  "email": null,
  "role": null,
  "expiresAt": null,
  "message": null,
} satisfies InviteResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as InviteResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


