
# InviteRequest

Request to invite a new team member.

## Properties

Name | Type
------------ | -------------
`email` | string
`role` | [TeamRole](TeamRole.md)
`name` | string

## Example

```typescript
import type { InviteRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "email": null,
  "role": null,
  "name": null,
} satisfies InviteRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as InviteRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


