
# VerificationResponse

Schema for verification response

## Properties

Name | Type
------------ | -------------
`isValid` | boolean
`isTampered` | boolean
`signatureValid` | boolean
`hashValid` | boolean
`confidenceScore` | number
`similarityScore` | number
`signerId` | string
`warnings` | Array&lt;string&gt;
`verificationTimeMs` | number
`createdAt` | Date

## Example

```typescript
import type { VerificationResponse } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "isValid": null,
  "isTampered": null,
  "signatureValid": null,
  "hashValid": null,
  "confidenceScore": null,
  "similarityScore": null,
  "signerId": null,
  "warnings": null,
  "verificationTimeMs": null,
  "createdAt": null,
} satisfies VerificationResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerificationResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


