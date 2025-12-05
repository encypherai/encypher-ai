
# LicensingInfo

Licensing information.

## Properties

Name | Type
------------ | -------------
`licenseType` | string
`licenseUrl` | string
`usageTerms` | string
`contactEmail` | string

## Example

```typescript
import type { LicensingInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "licenseType": null,
  "licenseUrl": null,
  "usageTerms": null,
  "contactEmail": null,
} satisfies LicensingInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as LicensingInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


