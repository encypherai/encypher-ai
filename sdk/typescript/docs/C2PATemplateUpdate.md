
# C2PATemplateUpdate

Request schema for updating an assertion template.

## Properties

Name | Type
------------ | -------------
`name` | string
`description` | string
`templateData` | { [key: string]: any; }
`category` | string
`isPublic` | boolean

## Example

```typescript
import type { C2PATemplateUpdate } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "name": null,
  "description": null,
  "templateData": null,
  "category": null,
  "isPublic": null,
} satisfies C2PATemplateUpdate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PATemplateUpdate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


