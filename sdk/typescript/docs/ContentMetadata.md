
# ContentMetadata

Schema for content metadata returned to AI companies.

## Properties

Name | Type
------------ | -------------
`id` | number
`contentType` | string
`wordCount` | number
`signedAt` | Date
`contentHash` | string
`verificationUrl` | string

## Example

```typescript
import type { ContentMetadata } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "contentType": null,
  "wordCount": null,
  "signedAt": null,
  "contentHash": null,
  "verificationUrl": null,
} satisfies ContentMetadata

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ContentMetadata
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


