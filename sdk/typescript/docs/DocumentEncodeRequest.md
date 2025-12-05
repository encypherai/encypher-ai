
# DocumentEncodeRequest

Request schema for encoding a document into Merkle trees.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`text` | string
`segmentationLevels` | Array&lt;string&gt;
`includeWords` | boolean
`metadata` | { [key: string]: any; }

## Example

```typescript
import type { DocumentEncodeRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": doc_2024_article_001,
  "text": This is the first sentence. This is the second sentence.,
  "segmentationLevels": [sentence, paragraph],
  "includeWords": null,
  "metadata": null,
} satisfies DocumentEncodeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as DocumentEncodeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


