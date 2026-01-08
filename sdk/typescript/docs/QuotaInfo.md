
# QuotaInfo

Detailed quota information.

## Properties

Name | Type
------------ | -------------
`organizationId` | string
`tier` | string
`periodStart` | string
`periodEnd` | string
`metrics` | [{ [key: string]: QuotaMetric; }](QuotaMetric.md)
`resetDate` | string

## Example

```typescript
import type { QuotaInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "organizationId": null,
  "tier": null,
  "periodStart": null,
  "periodEnd": null,
  "metrics": null,
  "resetDate": null,
} satisfies QuotaInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as QuotaInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


