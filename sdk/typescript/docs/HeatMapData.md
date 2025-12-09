
# HeatMapData

Schema for heat map visualization data.

## Properties

Name | Type
------------ | -------------
`positions` | Array&lt;{ [key: string]: any; }&gt;
`totalSegments` | number
`matchedSegments` | number
`matchPercentage` | number

## Example

```typescript
import type { HeatMapData } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "positions": null,
  "totalSegments": null,
  "matchedSegments": null,
  "matchPercentage": null,
} satisfies HeatMapData

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as HeatMapData
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


