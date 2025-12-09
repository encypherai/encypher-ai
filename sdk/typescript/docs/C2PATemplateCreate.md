
# C2PATemplateCreate

Request schema for creating an assertion template.

## Properties

Name | Type
------------ | -------------
`name` | string
`schemaId` | string
`templateData` | { [key: string]: any; }
`description` | string
`category` | string
`isPublic` | boolean

## Example

```typescript
import type { C2PATemplateCreate } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "name": null,
  "schemaId": null,
  "templateData": null,
  "description": null,
  "category": null,
  "isPublic": null,
} satisfies C2PATemplateCreate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PATemplateCreate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


