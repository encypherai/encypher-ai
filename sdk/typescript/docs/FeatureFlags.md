
# FeatureFlags

Organization feature flags.

## Properties

Name | Type
------------ | -------------
`merkleEnabled` | boolean
`byokEnabled` | boolean
`sentenceTracking` | boolean
`bulkOperations` | boolean
`customAssertions` | boolean
`streaming` | boolean
`teamManagement` | boolean
`auditLogs` | boolean
`sso` | boolean
`maxTeamMembers` | number

## Example

```typescript
import type { FeatureFlags } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "merkleEnabled": null,
  "byokEnabled": null,
  "sentenceTracking": null,
  "bulkOperations": null,
  "customAssertions": null,
  "streaming": null,
  "teamManagement": null,
  "auditLogs": null,
  "sso": null,
  "maxTeamMembers": null,
} satisfies FeatureFlags

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as FeatureFlags
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


