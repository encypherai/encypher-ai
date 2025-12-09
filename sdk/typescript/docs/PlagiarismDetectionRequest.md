
# PlagiarismDetectionRequest

Request schema for plagiarism detection.

## Properties

Name | Type
------------ | -------------
`targetText` | string
`targetDocumentId` | string
`segmentationLevel` | string
`includeHeatMap` | boolean
`minMatchPercentage` | number

## Example

```typescript
import type { PlagiarismDetectionRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "targetText": null,
  "targetDocumentId": null,
  "segmentationLevel": null,
  "includeHeatMap": null,
  "minMatchPercentage": null,
} satisfies PlagiarismDetectionRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PlagiarismDetectionRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


