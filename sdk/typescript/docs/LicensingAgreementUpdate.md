
# LicensingAgreementUpdate

Schema for updating a licensing agreement.

## Properties

Name | Type
------------ | -------------
`agreementName` | string
`totalValue` | [TotalValue1](TotalValue1.md)
`endDate` | Date
`contentTypes` | Array&lt;string&gt;
`minWordCount` | number
`status` | [AgreementStatus](AgreementStatus.md)

## Example

```typescript
import type { LicensingAgreementUpdate } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "agreementName": null,
  "totalValue": null,
  "endDate": null,
  "contentTypes": null,
  "minWordCount": null,
  "status": null,
} satisfies LicensingAgreementUpdate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as LicensingAgreementUpdate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


