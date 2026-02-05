
# SignOptions

Options for signing - features are gated by tier.  Tier Feature Matrix:  | Feature                  | Free/Starter | Professional | Business | Enterprise | |--------------------------|--------------|--------------|----------|------------| | document_type            | ✅           | ✅           | ✅       | ✅         | | claim_generator          | ✅           | ✅           | ✅       | ✅         | | segmentation_level       | document     | all          | all      | all        | | manifest_mode            | full         | all          | all      | all        | | embedding_strategy       | single_point | all          | all      | all        | | index_for_attribution    | ❌           | ✅           | ✅       | ✅         | | custom_assertions        | ❌           | ❌           | ✅       | ✅         | | template_id              | ❌           | ❌           | ✅       | ✅         | | rights                   | ❌           | ❌           | ✅       | ✅         | | add_dual_binding         | ❌           | ❌           | ❌       | ✅         | | include_fingerprint      | ❌           | ❌           | ❌       | ✅         | | batch (documents array)  | 1            | 10           | 50       | 100        |

## Properties

Name | Type
------------ | -------------
`documentType` | string
`claimGenerator` | string
`action` | string
`previousInstanceId` | string
`digitalSourceType` | string
`segmentationLevel` | string
`segmentationLevels` | Array&lt;string&gt;
`manifestMode` | string
`embeddingStrategy` | string
`distributionTarget` | string
`indexForAttribution` | boolean
`customAssertions` | Array&lt;{ [key: string]: any; }&gt;
`templateId` | string
`validateAssertions` | boolean
`rights` | [RightsMetadata](RightsMetadata.md)
`license` | [LicenseInfo](LicenseInfo.md)
`actions` | Array&lt;{ [key: string]: any; }&gt;
`addDualBinding` | boolean
`includeFingerprint` | boolean
`disableC2pa` | boolean
`embeddingOptions` | [EmbeddingOptions](EmbeddingOptions.md)
`expiresAt` | Date

## Example

```typescript
import type { SignOptions } from '@encypher/sdk'

// TODO: Update the object below with actual values
const example = {
  "documentType": null,
  "claimGenerator": null,
  "action": null,
  "previousInstanceId": null,
  "digitalSourceType": null,
  "segmentationLevel": null,
  "segmentationLevels": null,
  "manifestMode": null,
  "embeddingStrategy": null,
  "distributionTarget": null,
  "indexForAttribution": null,
  "customAssertions": null,
  "templateId": null,
  "validateAssertions": null,
  "rights": null,
  "license": null,
  "actions": null,
  "addDualBinding": null,
  "includeFingerprint": null,
  "disableC2pa": null,
  "embeddingOptions": null,
  "expiresAt": null,
} satisfies SignOptions

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SignOptions
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


