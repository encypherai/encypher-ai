
# DocumentEncodeResponse

Response schema for document encoding.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`message` | string
`documentId` | string
`organizationId` | string
`roots` | [{ [key: string]: MerkleRootResponse; }](MerkleRootResponse.md)
`totalSegments` | { [key: string]: number; }
`processingTimeMs` | number
`fuzzyIndex` | { [key: string]: any; }

## Example

```typescript
import type { DocumentEncodeResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "message": null,
  "documentId": null,
  "organizationId": null,
  "roots": null,
  "totalSegments": null,
  "processingTimeMs": null,
  "fuzzyIndex": null,
} satisfies DocumentEncodeResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as DocumentEncodeResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


