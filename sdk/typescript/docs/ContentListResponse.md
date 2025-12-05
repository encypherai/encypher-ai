
# ContentListResponse

Schema for listing available content.

## Properties

Name | Type
------------ | -------------
`content` | [Array&lt;ContentMetadata&gt;](ContentMetadata.md)
`total` | number
`quotaRemaining` | number

## Example

```typescript
import type { ContentListResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "content": null,
  "total": null,
  "quotaRemaining": null,
} satisfies ContentListResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ContentListResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


