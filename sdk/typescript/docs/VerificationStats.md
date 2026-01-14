
# VerificationStats

Schema for verification statistics

## Properties

Name | Type
------------ | -------------
`totalVerifications` | number
`validVerifications` | number
`invalidVerifications` | number
`tamperedDocuments` | number
`averageConfidenceScore` | number
`averageVerificationTimeMs` | number

## Example

```typescript
import type { VerificationStats } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "totalVerifications": null,
  "validVerifications": null,
  "invalidVerifications": null,
  "tamperedDocuments": null,
  "averageConfidenceScore": null,
  "averageVerificationTimeMs": null,
} satisfies VerificationStats

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as VerificationStats
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


