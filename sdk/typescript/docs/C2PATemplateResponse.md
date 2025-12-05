
# C2PATemplateResponse

Response schema for assertion template.

## Properties

Name | Type
------------ | -------------
`id` | string
`name` | string
`description` | string
`schemaId` | string
`templateData` | { [key: string]: any; }
`category` | string
`organizationId` | string
`isDefault` | boolean
`isActive` | boolean
`isPublic` | boolean
`createdAt` | string
`updatedAt` | string

## Example

```typescript
import type { C2PATemplateResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "name": null,
  "description": null,
  "schemaId": null,
  "templateData": null,
  "category": null,
  "organizationId": null,
  "isDefault": null,
  "isActive": null,
  "isPublic": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies C2PATemplateResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PATemplateResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


