
# LicensingAgreementCreateResponse

Schema for licensing agreement creation response (includes API key).

## Properties

Name | Type
------------ | -------------
`id` | string
`agreementName` | string
`apiKey` | string
`apiKeyPrefix` | string
`status` | [AgreementStatus](AgreementStatus.md)
`createdAt` | Date

## Example

```typescript
import type { LicensingAgreementCreateResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "agreementName": null,
  "apiKey": null,
  "apiKeyPrefix": null,
  "status": null,
  "createdAt": null,
} satisfies LicensingAgreementCreateResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as LicensingAgreementCreateResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


