
# DocumentInfo

Document information from verification.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`title` | string
`publishedAt` | Date
`author` | string
`organization` | string

## Example

```typescript
import type { DocumentInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "title": null,
  "publishedAt": null,
  "author": null,
  "organization": null,
} satisfies DocumentInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as DocumentInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


