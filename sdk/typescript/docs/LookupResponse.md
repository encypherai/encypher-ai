
# LookupResponse

Response model for sentence lookup operation.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`found` | boolean
`documentTitle` | string
`organizationName` | string
`publicationDate` | Date
`sentenceIndex` | number
`documentUrl` | string

## Example

```typescript
import type { LookupResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "found": null,
  "documentTitle": null,
  "organizationName": null,
  "publicationDate": null,
  "sentenceIndex": null,
  "documentUrl": null,
} satisfies LookupResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as LookupResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


