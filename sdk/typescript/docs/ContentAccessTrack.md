
# ContentAccessTrack

Schema for tracking content access.

## Properties

Name | Type
------------ | -------------
`contentId` | number
`accessType` | string

## Example

```typescript
import type { ContentAccessTrack } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "contentId": null,
  "accessType": null,
} satisfies ContentAccessTrack

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ContentAccessTrack
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


