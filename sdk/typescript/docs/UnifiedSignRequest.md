
# UnifiedSignRequest

Unified sign request supporting single document or batch.  For single document signing: ```json {     \"text\": \"Content to sign...\",     \"document_title\": \"My Article\",     \"options\": {         \"segmentation_level\": \"sentence\"     } } ```  For batch signing (Professional+): ```json {     \"documents\": [         {\"text\": \"First document...\", \"document_title\": \"Doc 1\"},         {\"text\": \"Second document...\", \"document_title\": \"Doc 2\"}     ],     \"options\": {         \"segmentation_level\": \"sentence\"     } } ```

## Properties

Name | Type
------------ | -------------
`text` | string
`documentId` | string
`documentTitle` | string
`documentUrl` | string
`metadata` | { [key: string]: any; }
`documents` | [Array&lt;SignDocument&gt;](SignDocument.md)
`options` | [SignOptions](SignOptions.md)

## Example

```typescript
import type { UnifiedSignRequest } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "text": null,
  "documentId": null,
  "documentTitle": null,
  "documentUrl": null,
  "metadata": null,
  "documents": null,
  "options": null,
} satisfies UnifiedSignRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as UnifiedSignRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


