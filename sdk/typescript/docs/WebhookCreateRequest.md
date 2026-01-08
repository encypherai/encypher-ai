
# WebhookCreateRequest

Request to create a webhook.

## Properties

Name | Type
------------ | -------------
`url` | string
`events` | Array&lt;string&gt;
`secret` | string

## Example

```typescript
import type { WebhookCreateRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "url": null,
  "events": null,
  "secret": null,
} satisfies WebhookCreateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as WebhookCreateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


