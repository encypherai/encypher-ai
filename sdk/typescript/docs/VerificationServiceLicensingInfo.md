
# VerificationServiceLicensingInfo

Content licensing information.

## Properties

Name | Type
------------ | -------------
`licenseType` | string
`licenseUrl` | string
`usageTerms` | string
`attributionRequired` | boolean

## Example

```typescript
import type { VerificationServiceLicensingInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "licenseType": null,
  "licenseUrl": null,
  "usageTerms": null,
  "attributionRequired": null,
} satisfies VerificationServiceLicensingInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerificationServiceLicensingInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


