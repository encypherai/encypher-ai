
# VerificationServiceDocumentInfo

Document metadata from the embedding.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`title` | string
`author` | string
`publishedAt` | Date
`documentType` | string

## Example

```typescript
import type { VerificationServiceDocumentInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "title": null,
  "author": null,
  "publishedAt": null,
  "documentType": null,
} satisfies VerificationServiceDocumentInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerificationServiceDocumentInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


