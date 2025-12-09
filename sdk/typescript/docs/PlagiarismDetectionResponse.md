
# PlagiarismDetectionResponse

Response schema for plagiarism detection.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`reportId` | string
`targetDocumentId` | string
`totalSegments` | number
`matchedSegments` | number
`overallMatchPercentage` | number
`sourceDocuments` | [Array&lt;SourceDocumentMatch&gt;](SourceDocumentMatch.md)
`heatMapData` | [HeatMapData](HeatMapData.md)
`processingTimeMs` | number
`scanTimestamp` | Date

## Example

```typescript
import type { PlagiarismDetectionResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "reportId": null,
  "targetDocumentId": null,
  "totalSegments": null,
  "matchedSegments": null,
  "overallMatchPercentage": null,
  "sourceDocuments": null,
  "heatMapData": null,
  "processingTimeMs": null,
  "scanTimestamp": null,
} satisfies PlagiarismDetectionResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PlagiarismDetectionResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


