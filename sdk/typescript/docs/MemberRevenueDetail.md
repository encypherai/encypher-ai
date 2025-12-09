
# MemberRevenueDetail

Schema for member revenue detail.

## Properties

Name | Type
------------ | -------------
`id` | string
`memberId` | string
`contentCount` | number
`accessCount` | number
`revenueAmount` | string
`status` | [PayoutStatus](PayoutStatus.md)
`paidAt` | Date
`paymentReference` | string

## Example

```typescript
import type { MemberRevenueDetail } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "memberId": null,
  "contentCount": null,
  "accessCount": null,
  "revenueAmount": null,
  "status": null,
  "paidAt": null,
  "paymentReference": null,
} satisfies MemberRevenueDetail

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MemberRevenueDetail
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


