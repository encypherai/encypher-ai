
# SourceAttributionResponse

Response schema for source attribution.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`queryHash` | string
`matchesFound` | number
`sources` | [Array&lt;SourceMatch&gt;](SourceMatch.md)
`processingTimeMs` | number

## Example

```typescript
import type { SourceAttributionResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "queryHash": null,
  "matchesFound": null,
  "sources": null,
  "processingTimeMs": null,
} satisfies SourceAttributionResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SourceAttributionResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


