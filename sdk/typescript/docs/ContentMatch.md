
# ContentMatch

Details of matched content.

## Properties

Name | Type
------------ | -------------
`segmentText` | string
`segmentHash` | string
`leafIndex` | number
`confidence` | number
`sourceDocumentId` | string
`sourceOrganizationId` | string

## Example

```typescript
import type { ContentMatch } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "segmentText": null,
  "segmentHash": null,
  "leafIndex": null,
  "confidence": null,
  "sourceDocumentId": null,
  "sourceOrganizationId": null,
} satisfies ContentMatch

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ContentMatch
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


