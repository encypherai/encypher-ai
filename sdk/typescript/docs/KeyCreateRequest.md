
# KeyCreateRequest

Request to create a new API key.

## Properties

Name | Type
------------ | -------------
`name` | string
`permissions` | Array&lt;string&gt;
`expiresInDays` | number

## Example

```typescript
import type { KeyCreateRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "name": null,
  "permissions": null,
  "expiresInDays": null,
} satisfies KeyCreateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as KeyCreateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


