
# C2PAInfo

C2PA manifest information with verification details.

## Properties

Name | Type
------------ | -------------
`manifestUrl` | string
`manifestHash` | string
`validated` | boolean
`validationType` | string
`validationDetails` | { [key: string]: any; }

## Example

```typescript
import type { C2PAInfo } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "manifestUrl": null,
  "manifestHash": null,
  "validated": null,
  "validationType": null,
  "validationDetails": null,
} satisfies C2PAInfo

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as C2PAInfo
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


