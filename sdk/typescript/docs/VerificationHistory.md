
# VerificationHistory

Schema for verification history

## Properties

Name | Type
------------ | -------------
`id` | string
`documentId` | string
`isValid` | boolean
`isTampered` | boolean
`confidenceScore` | number
`createdAt` | Date

## Example

```typescript
import type { VerificationHistory } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "documentId": null,
  "isValid": null,
  "isTampered": null,
  "confidenceScore": null,
  "createdAt": null,
} satisfies VerificationHistory

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerificationHistory
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


