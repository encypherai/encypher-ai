
# SignatureVerify

Schema for signature verification

## Properties

Name | Type
------------ | -------------
`content` | string
`signature` | string
`publicKeyPem` | string

## Example

```typescript
import type { SignatureVerify } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "content": null,
  "signature": null,
  "publicKeyPem": null,
} satisfies SignatureVerify

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SignatureVerify
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


