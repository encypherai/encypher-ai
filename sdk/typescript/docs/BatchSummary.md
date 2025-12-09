
# BatchSummary

Aggregated stats for the batch.

## Properties

Name | Type
------------ | -------------
`totalItems` | number
`successCount` | number
`failureCount` | number
`mode` | string
`status` | string
`durationMs` | number
`startedAt` | string
`completedAt` | string

## Example

```typescript
import type { BatchSummary } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "totalItems": null,
  "successCount": null,
  "failureCount": null,
  "mode": null,
  "status": null,
  "durationMs": null,
  "startedAt": null,
  "completedAt": null,
} satisfies BatchSummary

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BatchSummary
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


