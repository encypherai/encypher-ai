
# APIKeyCreateRequest

Request schema for creating an API key.

## Properties

Name | Type
------------ | -------------
`name` | string
`expiresInDays` | number
`scopes` | Array&lt;string&gt;

## Example

```typescript
import type { APIKeyCreateRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "name": null,
  "expiresInDays": null,
  "scopes": null,
} satisfies APIKeyCreateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as APIKeyCreateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


