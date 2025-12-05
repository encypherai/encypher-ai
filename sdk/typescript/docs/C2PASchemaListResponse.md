
# C2PASchemaListResponse

Response schema for listing C2PA schemas.

## Properties

Name | Type
------------ | -------------
`schemas` | [Array&lt;C2PASchemaResponse&gt;](C2PASchemaResponse.md)
`total` | number
`page` | number
`pageSize` | number

## Example

```typescript
import type { C2PASchemaListResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "schemas": null,
  "total": null,
  "page": null,
  "pageSize": null,
} satisfies C2PASchemaListResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PASchemaListResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


