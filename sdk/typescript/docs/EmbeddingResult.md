
# EmbeddingResult

Result for a single embedding found in text.

## Properties

Name | Type
------------ | -------------
`index` | number
`metadata` | { [key: string]: any; }
`verificationStatus` | string
`error` | string
`verdict` | [AppRoutersToolsVerifyVerdict](AppRoutersToolsVerifyVerdict.md)
`textSpan` | Array&lt;any&gt;
`cleanText` | string

## Example

```typescript
import type { EmbeddingResult } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "index": null,
  "metadata": null,
  "verificationStatus": null,
  "error": null,
  "verdict": null,
  "textSpan": null,
  "cleanText": null,
} satisfies EmbeddingResult

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EmbeddingResult
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


