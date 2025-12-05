
# UsageMetric

Single usage metric with limit info.

## Properties

Name | Type
------------ | -------------
`name` | string
`used` | number
`limit` | number
`remaining` | number
`percentageUsed` | number
`available` | boolean

## Example

```typescript
import type { UsageMetric } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "name": null,
  "used": null,
  "limit": null,
  "remaining": null,
  "percentageUsed": null,
  "available": null,
} satisfies UsageMetric

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as UsageMetric
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


