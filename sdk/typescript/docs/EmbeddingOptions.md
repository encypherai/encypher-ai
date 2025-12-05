
# EmbeddingOptions

Options for embedding generation.

## Properties

Name | Type
------------ | -------------
`format` | string
`method` | string
`includeText` | boolean

## Example

```typescript
import type { EmbeddingOptions } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "format": null,
  "method": null,
  "includeText": null,
} satisfies EmbeddingOptions

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EmbeddingOptions
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


