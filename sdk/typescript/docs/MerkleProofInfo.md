
# MerkleProofInfo

Merkle proof information.

## Properties

Name | Type
------------ | -------------
`rootHash` | string
`verified` | boolean
`proofUrl` | string

## Example

```typescript
import type { MerkleProofInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "rootHash": null,
  "verified": null,
  "proofUrl": null,
} satisfies MerkleProofInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MerkleProofInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


