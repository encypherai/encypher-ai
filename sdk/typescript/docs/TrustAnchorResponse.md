
# TrustAnchorResponse

Response for trust anchor lookup.  Enables external C2PA validators to verify Encypher-signed content by providing the signer\'s public key.  See: https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_trust_lists

## Properties

Name | Type
------------ | -------------
`signerId` | string
`signerName` | string
`publicKey` | string
`publicKeyAlgorithm` | string
`keyId` | string
`issuedAt` | string
`expiresAt` | string
`revoked` | boolean
`trustAnchorType` | string

## Example

```typescript
import type { TrustAnchorResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "signerId": null,
  "signerName": null,
  "publicKey": null,
  "publicKeyAlgorithm": null,
  "keyId": null,
  "issuedAt": null,
  "expiresAt": null,
  "revoked": null,
  "trustAnchorType": null,
} satisfies TrustAnchorResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TrustAnchorResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


