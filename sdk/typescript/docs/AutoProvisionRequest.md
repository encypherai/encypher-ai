
# AutoProvisionRequest

Request schema for auto-provisioning an organization and API key.

## Properties

Name | Type
------------ | -------------
`email` | string
`organizationName` | string
`source` | string
`sourceMetadata` | { [key: string]: any; }
`tier` | string
`autoActivate` | boolean

## Example

```typescript
import type { AutoProvisionRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "email": user@example.com,
  "organizationName": null,
  "source": wordpress,
  "sourceMetadata": null,
  "tier": null,
  "autoActivate": null,
} satisfies AutoProvisionRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AutoProvisionRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


