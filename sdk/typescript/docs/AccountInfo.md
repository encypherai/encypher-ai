
# AccountInfo

Organization account information.

## Properties

Name | Type
------------ | -------------
`organizationId` | string
`name` | string
`email` | string
`tier` | string
`features` | [FeatureFlags](FeatureFlags.md)
`createdAt` | string
`subscriptionStatus` | string

## Example

```typescript
import type { AccountInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "organizationId": null,
  "name": null,
  "email": null,
  "tier": null,
  "features": null,
  "createdAt": null,
  "subscriptionStatus": null,
} satisfies AccountInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AccountInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


