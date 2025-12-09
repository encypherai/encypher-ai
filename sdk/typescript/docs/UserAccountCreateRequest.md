
# UserAccountCreateRequest

Request schema for creating a user account.

## Properties

Name | Type
------------ | -------------
`email` | string
`fullName` | string
`organizationId` | string
`role` | string
`sendWelcomeEmail` | boolean

## Example

```typescript
import type { UserAccountCreateRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "email": null,
  "fullName": null,
  "organizationId": null,
  "role": null,
  "sendWelcomeEmail": null,
} satisfies UserAccountCreateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as UserAccountCreateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


