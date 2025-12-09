
# C2PAAssertionValidationResult

Validation result for a single assertion.

## Properties

Name | Type
------------ | -------------
`label` | string
`valid` | boolean
`errors` | Array&lt;string&gt;
`warnings` | Array&lt;string&gt;

## Example

```typescript
import type { C2PAAssertionValidationResult } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "label": null,
  "valid": null,
  "errors": null,
  "warnings": null,
} satisfies C2PAAssertionValidationResult

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PAAssertionValidationResult
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


