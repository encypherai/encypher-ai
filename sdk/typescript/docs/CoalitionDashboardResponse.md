
# CoalitionDashboardResponse

Coalition dashboard data.

## Properties

Name | Type
------------ | -------------
`organizationId` | string
`tier` | string
`publisherSharePercent` | number
`coalitionMember` | boolean
`optedOut` | boolean
`currentPeriod` | [ContentStats](ContentStats.md)
`lifetimeEarningsCents` | number
`pendingEarningsCents` | number
`paidEarningsCents` | number
`recentEarnings` | [Array&lt;EarningsSummary&gt;](EarningsSummary.md)
`recentPayouts` | [Array&lt;PayoutSummary&gt;](PayoutSummary.md)

## Example

```typescript
import type { CoalitionDashboardResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "organizationId": null,
  "tier": null,
  "publisherSharePercent": null,
  "coalitionMember": null,
  "optedOut": null,
  "currentPeriod": null,
  "lifetimeEarningsCents": null,
  "pendingEarningsCents": null,
  "paidEarningsCents": null,
  "recentEarnings": null,
  "recentPayouts": null,
} satisfies CoalitionDashboardResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CoalitionDashboardResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


