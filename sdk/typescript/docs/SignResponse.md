
# SignResponse

Response model for signing operation.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`documentId` | string
`signedText` | string
`totalSentences` | number
`verificationUrl` | string

## Example

```typescript
import type { SignResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "documentId": null,
  "signedText": null,
  "totalSentences": null,
  "verificationUrl": null,
} satisfies SignResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SignResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


