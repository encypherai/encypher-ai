
# LicensingAgreementResponse

Schema for licensing agreement response.

## Properties

Name | Type
------------ | -------------
`id` | string
`agreementName` | string
`aiCompanyId` | string
`agreementType` | [AgreementType](AgreementType.md)
`totalValue` | string
`currency` | string
`startDate` | Date
`endDate` | Date
`contentTypes` | Array&lt;string&gt;
`minWordCount` | number
`status` | [AgreementStatus](AgreementStatus.md)
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { LicensingAgreementResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "agreementName": null,
  "aiCompanyId": null,
  "agreementType": null,
  "totalValue": null,
  "currency": null,
  "startDate": null,
  "endDate": null,
  "contentTypes": null,
  "minWordCount": null,
  "status": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies LicensingAgreementResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as LicensingAgreementResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


