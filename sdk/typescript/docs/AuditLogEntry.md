
# AuditLogEntry

Single audit log entry.

## Properties

Name | Type
------------ | -------------
`id` | string
`timestamp` | string
`action` | string
`actorId` | string
`actorType` | string
`resourceType` | string
`resourceId` | string
`details` | { [key: string]: any; }
`ipAddress` | string
`userAgent` | string

## Example

```typescript
import type { AuditLogEntry } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "timestamp": null,
  "action": null,
  "actorId": null,
  "actorType": null,
  "resourceType": null,
  "resourceId": null,
  "details": null,
  "ipAddress": null,
  "userAgent": null,
} satisfies AuditLogEntry

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AuditLogEntry
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


