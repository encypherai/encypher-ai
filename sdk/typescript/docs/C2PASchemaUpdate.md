
# C2PASchemaUpdate

Request schema for updating a C2PA assertion schema.

## Properties

Name | Type
------------ | -------------
`jsonSchema` | { [key: string]: any; }
`description` | string
`isPublic` | boolean

## Example

```typescript
import type { C2PASchemaUpdate } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "jsonSchema": null,
  "description": null,
  "isPublic": null,
} satisfies C2PASchemaUpdate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PASchemaUpdate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


