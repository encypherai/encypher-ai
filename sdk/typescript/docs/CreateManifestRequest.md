
# CreateManifestRequest


## Properties

Name | Type
------------ | -------------
`text` | string
`filename` | string
`documentTitle` | string
`claimGenerator` | string

## Example

```typescript
import type { CreateManifestRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "text": null,
  "filename": null,
  "documentTitle": null,
  "claimGenerator": null,
} satisfies CreateManifestRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CreateManifestRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


