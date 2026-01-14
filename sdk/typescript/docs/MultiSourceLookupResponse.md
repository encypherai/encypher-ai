
# MultiSourceLookupResponse

Response containing multi-source lookup results.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`queryHash` | string
`totalSources` | number
`sources` | [Array&lt;SourceRecord&gt;](SourceRecord.md)
`originalSource` | [SourceRecord](SourceRecord.md)
`hasChain` | boolean
`chainLength` | number
`processingTimeMs` | number
`message` | string

## Example

```typescript
import type { MultiSourceLookupResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "queryHash": null,
  "totalSources": null,
  "sources": null,
  "originalSource": null,
  "hasChain": null,
  "chainLength": null,
  "processingTimeMs": null,
  "message": null,
} satisfies MultiSourceLookupResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MultiSourceLookupResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


