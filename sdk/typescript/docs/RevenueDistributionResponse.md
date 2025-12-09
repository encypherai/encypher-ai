
# RevenueDistributionResponse

Schema for revenue distribution response.

## Properties

Name | Type
------------ | -------------
`id` | string
`agreementId` | string
`periodStart` | Date
`periodEnd` | Date
`totalRevenue` | string
`encypherShare` | string
`memberPool` | string
`status` | [DistributionStatus](DistributionStatus.md)
`createdAt` | Date
`processedAt` | Date
`memberRevenues` | [Array&lt;MemberRevenueDetail&gt;](MemberRevenueDetail.md)

## Example

```typescript
import type { RevenueDistributionResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "agreementId": null,
  "periodStart": null,
  "periodEnd": null,
  "totalRevenue": null,
  "encypherShare": null,
  "memberPool": null,
  "status": null,
  "createdAt": null,
  "processedAt": null,
  "memberRevenues": null,
} satisfies RevenueDistributionResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RevenueDistributionResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


