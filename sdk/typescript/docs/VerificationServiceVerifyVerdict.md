
# VerificationServiceVerifyVerdict

Core verification result.

## Properties

Name | Type
------------ | -------------
`valid` | boolean
`tampered` | boolean
`reasonCode` | string
`signerId` | string
`signerName` | string
`organizationId` | string
`organizationName` | string
`timestamp` | Date
`document` | [DocumentInfo](DocumentInfo.md)
`c2pa` | [C2PAInfo](C2PAInfo.md)
`licensing` | [LicensingInfo](LicensingInfo.md)
`merkleProof` | [MerkleProofInfo](MerkleProofInfo.md)
`details` | { [key: string]: any; }

## Example

```typescript
import type { VerificationServiceVerifyVerdict } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "valid": null,
  "tampered": null,
  "reasonCode": null,
  "signerId": null,
  "signerName": null,
  "organizationId": null,
  "organizationName": null,
  "timestamp": null,
  "document": null,
  "c2pa": null,
  "licensing": null,
  "merkleProof": null,
  "details": null,
} satisfies VerificationServiceVerifyVerdict

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerificationServiceVerifyVerdict
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


