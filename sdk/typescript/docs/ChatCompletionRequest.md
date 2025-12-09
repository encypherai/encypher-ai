
# ChatCompletionRequest

OpenAI-compatible chat completion request.

## Properties

Name | Type
------------ | -------------
`messages` | [Array&lt;ChatMessage&gt;](ChatMessage.md)
`model` | string
`temperature` | number
`topP` | number
`n` | number
`stream` | boolean
`stop` | Array&lt;string&gt;
`maxTokens` | number
`presencePenalty` | number
`frequencyPenalty` | number
`user` | string
`signResponse` | boolean

## Example

```typescript
import type { ChatCompletionRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "messages": null,
  "model": null,
  "temperature": null,
  "topP": null,
  "n": null,
  "stream": null,
  "stop": null,
  "maxTokens": null,
  "presencePenalty": null,
  "frequencyPenalty": null,
  "user": null,
  "signResponse": null,
} satisfies ChatCompletionRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ChatCompletionRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


