
# MerkleRootResponse

Response schema for a single Merkle root.

## Properties

Name | Type
------------ | -------------
`rootId` | string
`documentId` | string
`rootHash` | string
`treeDepth` | number
`totalLeaves` | number
`segmentationLevel` | string
`createdAt` | Date
`metadata` | { [key: string]: any; }

## Example

```typescript
import type { MerkleRootResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "rootId": null,
  "documentId": null,
  "rootHash": null,
  "treeDepth": null,
  "totalLeaves": null,
  "segmentationLevel": null,
  "createdAt": null,
  "metadata": null,
} satisfies MerkleRootResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MerkleRootResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


