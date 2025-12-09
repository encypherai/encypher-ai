
# C2PAAssertionValidateRequest

Request schema for validating a C2PA assertion.

## Properties

Name | Type
------------ | -------------
`label` | string
`data` | { [key: string]: any; }

## Example

```typescript
import type { C2PAAssertionValidateRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "label": null,
  "data": null,
} satisfies C2PAAssertionValidateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PAAssertionValidateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


