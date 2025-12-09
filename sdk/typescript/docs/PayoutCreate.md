
# PayoutCreate

Schema for processing payouts.

## Properties

Name | Type
------------ | -------------
`distributionId` | string
`paymentMethod` | string

## Example

```typescript
import type { PayoutCreate } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "distributionId": null,
  "paymentMethod": null,
} satisfies PayoutCreate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as PayoutCreate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


