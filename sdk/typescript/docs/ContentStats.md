
# ContentStats

Content corpus statistics.

## Properties

Name | Type
------------ | -------------
`periodStart` | string
`periodEnd` | string
`documentsCount` | number
`sentencesCount` | number
`totalCharacters` | number
`uniqueContentHashCount` | number
`contentCategories` | { [key: string]: any; }

## Example

```typescript
import type { ContentStats } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "periodStart": null,
  "periodEnd": null,
  "documentsCount": null,
  "sentencesCount": null,
  "totalCharacters": null,
  "uniqueContentHashCount": null,
  "contentCategories": null,
} satisfies ContentStats

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ContentStats
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


