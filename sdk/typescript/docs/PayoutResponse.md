
# PayoutResponse

Schema for payout response.

## Properties

Name | Type
------------ | -------------
`distributionId` | string
`totalMembersPaid` | number
`totalAmountPaid` | string
`failedPayments` | Array&lt;string&gt;

## Example

```typescript
import type { PayoutResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "distributionId": null,
  "totalMembersPaid": null,
  "totalAmountPaid": null,
  "failedPayments": null,
} satisfies PayoutResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PayoutResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


