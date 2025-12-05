
# PayoutSummary

Payout summary.

## Properties

Name | Type
------------ | -------------
`id` | string
`periodStart` | string
`periodEnd` | string
`totalEarningsCents` | number
`payoutAmountCents` | number
`currency` | string
`status` | string
`paidAt` | string

## Example

```typescript
import type { PayoutSummary } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "periodStart": null,
  "periodEnd": null,
  "totalEarningsCents": null,
  "payoutAmountCents": null,
  "currency": null,
  "status": null,
  "paidAt": null,
} satisfies PayoutSummary

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PayoutSummary
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


