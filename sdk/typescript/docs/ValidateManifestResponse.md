
# ValidateManifestResponse


## Properties

Name | Type
------------ | -------------
`valid` | boolean
`errors` | Array&lt;string&gt;
`warnings` | Array&lt;string&gt;
`assertions` | [Array&lt;C2PAAssertionValidationResult&gt;](C2PAAssertionValidationResult.md)

## Example

```typescript
import type { ValidateManifestResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "valid": null,
  "errors": null,
  "warnings": null,
  "assertions": null,
} satisfies ValidateManifestResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ValidateManifestResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


