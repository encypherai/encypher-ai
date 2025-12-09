
# LicensingAgreementCreate

Schema for creating a licensing agreement.

## Properties

Name | Type
------------ | -------------
`agreementName` | string
`aiCompanyName` | string
`aiCompanyEmail` | string
`agreementType` | [AgreementType](AgreementType.md)
`totalValue` | [TotalValue](TotalValue.md)
`currency` | string
`startDate` | Date
`endDate` | Date
`contentTypes` | Array&lt;string&gt;
`minWordCount` | number

## Example

```typescript
import type { LicensingAgreementCreate } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "agreementName": null,
  "aiCompanyName": null,
  "aiCompanyEmail": null,
  "agreementType": null,
  "totalValue": null,
  "currency": null,
  "startDate": null,
  "endDate": null,
  "contentTypes": null,
  "minWordCount": null,
} satisfies LicensingAgreementCreate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as LicensingAgreementCreate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


