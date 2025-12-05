
# ChatMessage

Chat message in OpenAI format.

## Properties

Name | Type
------------ | -------------
`role` | string
`content` | string
`name` | string

## Example

```typescript
import type { ChatMessage } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "role": null,
  "content": null,
  "name": null,
} satisfies ChatMessage

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ChatMessage
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


