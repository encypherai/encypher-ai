
# PublicKeyInfo

Information about a registered public key.

## Properties

Name | Type
------------ | -------------
`id` | string
`organizationId` | string
`keyName` | string
`keyAlgorithm` | string
`keyFingerprint` | string
`publicKeyPem` | string
`isActive` | boolean
`createdAt` | Date
`lastUsedAt` | Date

## Example

```typescript
import type { PublicKeyInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "organizationId": null,
  "keyName": null,
  "keyAlgorithm": null,
  "keyFingerprint": null,
  "publicKeyPem": null,
  "isActive": null,
  "createdAt": null,
  "lastUsedAt": null,
} satisfies PublicKeyInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PublicKeyInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


