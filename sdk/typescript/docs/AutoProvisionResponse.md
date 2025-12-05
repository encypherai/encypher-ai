
# AutoProvisionResponse

Response schema for auto-provisioning.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`message` | string
`organizationId` | string
`organizationName` | string
`userId` | string
`apiKey` | [APIKeyResponse](APIKeyResponse.md)
`tier` | string
`featuresEnabled` | { [key: string]: boolean; }
`quotaLimits` | { [key: string]: number; }
`nextSteps` | { [key: string]: string; }

## Example

```typescript
import type { AutoProvisionResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "message": null,
  "organizationId": null,
  "organizationName": null,
  "userId": null,
  "apiKey": null,
  "tier": null,
  "featuresEnabled": null,
  "quotaLimits": null,
  "nextSteps": null,
} satisfies AutoProvisionResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AutoProvisionResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


