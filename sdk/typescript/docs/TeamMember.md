
# TeamMember

Team member details.

## Properties

Name | Type
------------ | -------------
`id` | string
`userId` | string
`email` | string
`name` | string
`role` | [TeamRole](TeamRole.md)
`status` | string
`invitedAt` | string
`acceptedAt` | string
`lastActiveAt` | string

## Example

```typescript
import type { TeamMember } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "userId": null,
  "email": null,
  "name": null,
  "role": null,
  "status": null,
  "invitedAt": null,
  "acceptedAt": null,
  "lastActiveAt": null,
} satisfies TeamMember

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TeamMember
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


