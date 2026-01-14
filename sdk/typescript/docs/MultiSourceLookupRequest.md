
# MultiSourceLookupRequest

Request to look up content across multiple sources.  Patent Reference: FIG. 8 - Multi-Source Hash Table Lookup

## Properties

Name | Type
------------ | -------------
`textSegment` | string
`includeAllSources` | boolean
`orderBy` | string
`includeAuthorityScore` | boolean
`maxResults` | number

## Example

```typescript
import type { MultiSourceLookupRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "textSegment": null,
  "includeAllSources": null,
  "orderBy": null,
  "includeAuthorityScore": null,
  "maxResults": null,
} satisfies MultiSourceLookupRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MultiSourceLookupRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


