
# SourceMatch

Schema for a single source match.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`organizationId` | string
`rootHash` | string
`segmentationLevel` | string
`matchedHash` | string
`textContent` | string
`confidence` | number

## Example

```typescript
import type { SourceMatch } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "organizationId": null,
  "rootHash": null,
  "segmentationLevel": null,
  "matchedHash": null,
  "textContent": null,
  "confidence": null,
} satisfies SourceMatch

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SourceMatch
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


