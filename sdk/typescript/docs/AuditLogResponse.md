
# AuditLogResponse

Paginated audit log response.

## Properties

Name | Type
------------ | -------------
`organizationId` | string
`logs` | [Array&lt;AuditLogEntry&gt;](AuditLogEntry.md)
`total` | number
`page` | number
`pageSize` | number
`hasMore` | boolean

## Example

```typescript
import type { AuditLogResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "organizationId": null,
  "logs": null,
  "total": null,
  "page": null,
  "pageSize": null,
  "hasMore": null,
} satisfies AuditLogResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AuditLogResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


