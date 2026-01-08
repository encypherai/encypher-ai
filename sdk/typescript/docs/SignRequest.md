
# SignRequest

Request model for signing content.

## Properties

Name | Type
------------ | -------------
`text` | string
`documentId` | string
`documentTitle` | string
`documentUrl` | string
`documentType` | string
`claimGenerator` | string
`actions` | Array&lt;{ [key: string]: any; }&gt;
`templateId` | string
`validateAssertions` | boolean
`rights` | [AppModelsRequestModelsRightsMetadata](AppModelsRequestModelsRightsMetadata.md)

## Example

```typescript
import type { SignRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "text": null,
  "documentId": null,
  "documentTitle": null,
  "documentUrl": null,
  "documentType": null,
  "claimGenerator": null,
  "actions": null,
  "templateId": null,
  "validateAssertions": null,
  "rights": null,
} satisfies SignRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SignRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


