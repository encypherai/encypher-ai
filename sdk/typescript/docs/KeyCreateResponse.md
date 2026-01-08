
# KeyCreateResponse

Response after creating a key (includes full key - only shown once).

## Properties

Name | Type
------------ | -------------
`success` | boolean
`data` | { [key: string]: any; }
`warning` | string

## Example

```typescript
import type { KeyCreateResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "success": null,
  "data": null,
  "warning": null,
} satisfies KeyCreateResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as KeyCreateResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


