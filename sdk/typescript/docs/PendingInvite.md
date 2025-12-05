
# PendingInvite

Pending team invitation.

## Properties

Name | Type
------------ | -------------
`id` | string
`email` | string
`role` | string
`invitedBy` | string
`status` | string
`expiresAt` | string
`createdAt` | string

## Example

```typescript
import type { PendingInvite } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "email": null,
  "role": null,
  "invitedBy": null,
  "status": null,
  "expiresAt": null,
  "createdAt": null,
} satisfies PendingInvite

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PendingInvite
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


