
# VerificationServiceC2PAInfo

C2PA manifest information.

## Properties

Name | Type
------------ | -------------
`manifestUrl` | string
`manifestHash` | string
`validated` | boolean
`validationType` | string
`assertions` | Array&lt;{ [key: string]: any; }&gt;
`certificateChain` | Array&lt;string&gt;

## Example

```typescript
import type { VerificationServiceC2PAInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "manifestUrl": null,
  "manifestHash": null,
  "validated": null,
  "validationType": null,
  "assertions": null,
  "certificateChain": null,
} satisfies VerificationServiceC2PAInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerificationServiceC2PAInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


