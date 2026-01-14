
# SignatureVerification

Signature verification details.

## Properties

Name | Type
------------ | -------------
`signerId` | string
`signerName` | string
`algorithm` | string
`publicKeyFingerprint` | string
`signatureValid` | boolean
`signedAt` | Date

## Example

```typescript
import type { SignatureVerification } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "signerId": null,
  "signerName": null,
  "algorithm": null,
  "publicKeyFingerprint": null,
  "signatureValid": null,
  "signedAt": null,
} satisfies SignatureVerification

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SignatureVerification
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


