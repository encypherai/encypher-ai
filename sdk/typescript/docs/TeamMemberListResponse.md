
# TeamMemberListResponse

List of team members.

## Properties

Name | Type
------------ | -------------
`organizationId` | string
`members` | [Array&lt;TeamMember&gt;](TeamMember.md)
`total` | number
`maxMembers` | number

## Example

```typescript
import type { TeamMemberListResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "organizationId": null,
  "members": null,
  "total": null,
  "maxMembers": null,
} satisfies TeamMemberListResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TeamMemberListResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


