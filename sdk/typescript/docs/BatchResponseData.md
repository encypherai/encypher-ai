
# BatchResponseData

Top-level data payload for batch responses.

## Properties

Name | Type
------------ | -------------
`results` | [Array&lt;BatchItemResult&gt;](BatchItemResult.md)
`summary` | [BatchSummary](BatchSummary.md)

## Example

```typescript
import type { BatchResponseData } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "results": null,
  "summary": null,
} satisfies BatchResponseData

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BatchResponseData
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


