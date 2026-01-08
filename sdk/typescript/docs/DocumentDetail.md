
# DocumentDetail

Detailed document information.

## Properties

Name | Type
------------ | -------------
`documentId` | string
`title` | string
`documentType` | string
`status` | string
`signedAt` | string
`verificationUrl` | string
`wordCount` | number
`url` | string
`signerId` | string
`revokedAt` | string
`revokedReason` | string

## Example

```typescript
import type { DocumentDetail } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentId": null,
  "title": null,
  "documentType": null,
  "status": null,
  "signedAt": null,
  "verificationUrl": null,
  "wordCount": null,
  "url": null,
  "signerId": null,
  "revokedAt": null,
  "revokedReason": null,
} satisfies DocumentDetail

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as DocumentDetail
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


