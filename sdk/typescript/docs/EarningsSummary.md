
# EarningsSummary

Earnings summary for a period.

## Properties

Name | Type
------------ | -------------
`periodStart` | string
`periodEnd` | string
`grossRevenueCents` | number
`publisherSharePercent` | number
`publisherEarningsCents` | number
`status` | string
`dealCount` | number

## Example

```typescript
import type { EarningsSummary } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "periodStart": null,
  "periodEnd": null,
  "grossRevenueCents": null,
  "publisherSharePercent": null,
  "publisherEarningsCents": null,
  "status": null,
  "dealCount": null,
} satisfies EarningsSummary

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EarningsSummary
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


