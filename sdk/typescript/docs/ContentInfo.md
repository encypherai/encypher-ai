
# ContentInfo

Content information from verification.

## Properties

Name | Type
------------ | -------------
`textPreview` | string
`leafHash` | string
`leafIndex` | number

## Example

```typescript
import type { ContentInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "textPreview": null,
  "leafHash": null,
  "leafIndex": null,
} satisfies ContentInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ContentInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


