
# UserAccountResponse

Response schema for user account.

## Properties

Name | Type
------------ | -------------
`userId` | string
`email` | string
`fullName` | string
`organizationId` | string
`role` | string
`createdAt` | Date
`isActive` | boolean

## Example

```typescript
import type { UserAccountResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "userId": null,
  "email": null,
  "fullName": null,
  "organizationId": null,
  "role": null,
  "createdAt": null,
  "isActive": null,
} satisfies UserAccountResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as UserAccountResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


