
# AppSchemasEmbeddingsBatchVerifyRequest

Request to verify multiple embeddings.

## Properties

Name | Type
------------ | -------------
`references` | [Array&lt;VerifyEmbeddingRequest&gt;](VerifyEmbeddingRequest.md)

## Example

```typescript
import type { AppSchemasEmbeddingsBatchVerifyRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "references": null,
} satisfies AppSchemasEmbeddingsBatchVerifyRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AppSchemasEmbeddingsBatchVerifyRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


