
# VerificationServiceMerkleProofInfo

Merkle tree proof information (paid feature).

## Properties

Name | Type
------------ | -------------
`rootHash` | string
`leafHash` | string
`leafIndex` | number
`proofPath` | Array&lt;string&gt;
`verified` | boolean

## Example

```typescript
import type { VerificationServiceMerkleProofInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "rootHash": null,
  "leafHash": null,
  "leafIndex": null,
  "proofPath": null,
  "verified": null,
} satisfies VerificationServiceMerkleProofInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerificationServiceMerkleProofInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


