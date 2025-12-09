
# AppRoutersToolsVerifyVerdict

Verification verdict details.

## Properties

Name | Type
------------ | -------------
`valid` | boolean
`tampered` | boolean
`reasonCode` | string
`signerId` | string
`signerName` | string
`timestamp` | string

## Example

```typescript
import type { AppRoutersToolsVerifyVerdict } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "valid": null,
  "tampered": null,
  "reasonCode": null,
  "signerId": null,
  "signerName": null,
  "timestamp": null,
} satisfies AppRoutersToolsVerifyVerdict

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AppRoutersToolsVerifyVerdict
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


