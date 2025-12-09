
# C2PASchemaResponse

Response schema for C2PA assertion schema.

## Properties

Name | Type
------------ | -------------
`id` | string
`name` | string
`label` | string
`version` | string
`jsonSchema` | { [key: string]: any; }
`description` | string
`organizationId` | string
`isActive` | boolean
`isPublic` | boolean
`createdAt` | string
`updatedAt` | string

## Example

```typescript
import type { C2PASchemaResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "name": null,
  "label": null,
  "version": null,
  "jsonSchema": null,
  "description": null,
  "organizationId": null,
  "isActive": null,
  "isPublic": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies C2PASchemaResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PASchemaResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


