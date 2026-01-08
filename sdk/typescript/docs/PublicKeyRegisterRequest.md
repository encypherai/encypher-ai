
# PublicKeyRegisterRequest

Request to register a BYOK public key.

## Properties

Name | Type
------------ | -------------
`publicKeyPem` | string
`keyName` | string
`keyAlgorithm` | string

## Example

```typescript
import type { PublicKeyRegisterRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "publicKeyPem": null,
  "keyName": null,
  "keyAlgorithm": null,
} satisfies PublicKeyRegisterRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PublicKeyRegisterRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


