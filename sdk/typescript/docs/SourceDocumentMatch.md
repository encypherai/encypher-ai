
# SourceDocumentMatch

Schema for a source document match in plagiarism report.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`organizationId` | string
`segmentationLevel` | string
`matchedSegments` | number
`totalLeaves` | number
`matchPercentage` | number
`confidenceScore` | number
`docMetadata` | { [key: string]: any; }

## Example

```typescript
import type { SourceDocumentMatch } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "organizationId": null,
  "segmentationLevel": null,
  "matchedSegments": null,
  "totalLeaves": null,
  "matchPercentage": null,
  "confidenceScore": null,
  "docMetadata": null,
} satisfies SourceDocumentMatch

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SourceDocumentMatch
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


