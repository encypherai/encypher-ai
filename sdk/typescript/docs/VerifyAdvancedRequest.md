
# VerifyAdvancedRequest


## Properties

Name | Type
------------ | -------------
`text` | string
`includeAttribution` | boolean
`detectPlagiarism` | boolean
`includeHeatMap` | boolean
`minMatchPercentage` | number
`segmentationLevel` | string
`searchScope` | string

## Example

```typescript
import type { VerifyAdvancedRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "text": null,
  "includeAttribution": null,
  "detectPlagiarism": null,
  "includeHeatMap": null,
  "minMatchPercentage": null,
  "segmentationLevel": null,
  "searchScope": null,
} satisfies VerifyAdvancedRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerifyAdvancedRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


