
# ValidateManifestRequest


## Properties

Name | Type
------------ | -------------
`manifest` | { [key: string]: any; }
`schemas` | { [key: string]: { [key: string]: any; }; }

## Example

```typescript
import type { ValidateManifestRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "manifest": null,
  "schemas": null,
} satisfies ValidateManifestRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ValidateManifestRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


