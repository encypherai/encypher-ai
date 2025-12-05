
# C2PATemplateListResponse

Response schema for listing templates.

## Properties

Name | Type
------------ | -------------
`templates` | [Array&lt;C2PATemplateResponse&gt;](C2PATemplateResponse.md)
`total` | number
`page` | number
`pageSize` | number

## Example

```typescript
import type { C2PATemplateListResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "templates": null,
  "total": null,
  "page": null,
  "pageSize": null,
} satisfies C2PATemplateListResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PATemplateListResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


