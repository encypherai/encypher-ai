
# EncodeToolRequest

Request model for encoding text with metadata.

## Properties

Name | Type
------------ | -------------
`originalText` | string
`target` | string
`metadataFormat` | string
`aiInfo` | { [key: string]: any; }
`customMetadata` | { [key: string]: any; }

## Example

```typescript
import type { EncodeToolRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "originalText": null,
  "target": null,
  "metadataFormat": null,
  "aiInfo": null,
  "customMetadata": null,
} satisfies EncodeToolRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EncodeToolRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


