
# EvidenceGenerateResponse

Response containing the generated evidence package.

## Properties

Name | Type
------------ | -------------
`success` | boolean
`evidence` | [EvidencePackage](EvidencePackage.md)
`processingTimeMs` | number
`message` | string

## Example

```typescript
import type { EvidenceGenerateResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "evidence": null,
  "processingTimeMs": null,
  "message": null,
} satisfies EvidenceGenerateResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EvidenceGenerateResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


