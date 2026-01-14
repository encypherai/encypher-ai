
# StreamMerkleFinalizeRequest

Request to finalize a streaming Merkle session and compute the final root.  This completes the tree construction, computes the final root hash, and optionally embeds a C2PA manifest into the full document.

## Properties

Name | Type
------------ | -------------
`sessionId` | string
`embedManifest` | boolean
`manifestMode` | string
`action` | string

## Example

```typescript
import type { StreamMerkleFinalizeRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "sessionId": null,
  "embedManifest": null,
  "manifestMode": null,
  "action": null,
} satisfies StreamMerkleFinalizeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StreamMerkleFinalizeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


