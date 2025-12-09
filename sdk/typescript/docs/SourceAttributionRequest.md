
# SourceAttributionRequest

Request schema for finding source documents.

## Properties

Name | Type
------------ | -------------
`textSegment` | string
`segmentationLevel` | string
`normalize` | boolean
`includeProof` | boolean

## Example

```typescript
import type { SourceAttributionRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "textSegment": This is a sentence to find.,
  "segmentationLevel": sentence,
  "normalize": null,
  "includeProof": null,
} satisfies SourceAttributionRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SourceAttributionRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


