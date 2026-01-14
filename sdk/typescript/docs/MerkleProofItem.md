
# MerkleProofItem

A single item in a Merkle proof path.

## Properties

Name | Type
------------ | -------------
`hash` | string
`position` | string
`level` | number

## Example

```typescript
import type { MerkleProofItem } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "hash": null,
  "position": null,
  "level": null,
} satisfies MerkleProofItem

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MerkleProofItem
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


