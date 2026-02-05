# SignOptions

Options for signing - features are gated by tier.  Tier Feature Matrix:  | Feature                  | Free/Starter | Professional | Business | Enterprise | |--------------------------|--------------|--------------|----------|------------| | document_type            | ✅           | ✅           | ✅       | ✅         | | claim_generator          | ✅           | ✅           | ✅       | ✅         | | segmentation_level       | document     | all          | all      | all        | | manifest_mode            | full         | all          | all      | all        | | embedding_strategy       | single_point | all          | all      | all        | | index_for_attribution    | ❌           | ✅           | ✅       | ✅         | | custom_assertions        | ❌           | ❌           | ✅       | ✅         | | template_id              | ❌           | ❌           | ✅       | ✅         | | rights                   | ❌           | ❌           | ✅       | ✅         | | add_dual_binding         | ❌           | ❌           | ❌       | ✅         | | include_fingerprint      | ❌           | ❌           | ❌       | ✅         | | batch (documents array)  | 1            | 10           | 50       | 100        |

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_type** | **str** | Document type: article, legal_brief, contract, ai_output | [optional] [default to 'article']
**claim_generator** | **str** |  | [optional] 
**action** | **str** | C2PA action type: c2pa.created (new) or c2pa.edited (modified) | [optional] [default to 'c2pa.created']
**previous_instance_id** | **str** |  | [optional] 
**digital_source_type** | **str** |  | [optional] 
**segmentation_level** | **str** | Segmentation level: document (free), sentence, paragraph, section (Professional+), word (Enterprise) | [optional] [default to 'document']
**segmentation_levels** | **List[str]** |  | [optional] 
**manifest_mode** | **str** | Manifest mode: full (free), lightweight_uuid, minimal_uuid, hybrid, zw_embedding (Professional+) | [optional] [default to 'full']
**embedding_strategy** | **str** | Embedding strategy: single_point (free), distributed, distributed_redundant (Professional+) | [optional] [default to 'single_point']
**distribution_target** | **str** |  | [optional] 
**index_for_attribution** | **bool** | Index content for attribution/plagiarism detection (Professional+) | [optional] [default to False]
**custom_assertions** | **List[Dict[str, object]]** |  | [optional] 
**template_id** | **str** |  | [optional] 
**validate_assertions** | **bool** | Whether to validate custom assertions against registered schemas (Business+) | [optional] [default to True]
**rights** | [**RightsMetadata**](RightsMetadata.md) |  | [optional] 
**license** | [**LicenseInfo**](LicenseInfo.md) |  | [optional] 
**actions** | **List[Dict[str, object]]** |  | [optional] 
**add_dual_binding** | **bool** | Enable additional integrity binding (Enterprise) | [optional] [default to False]
**include_fingerprint** | **bool** | Include robust fingerprint that survives modifications (Enterprise) | [optional] [default to False]
**disable_c2pa** | **bool** | Opt-out of C2PA embedding, only basic metadata (Enterprise) | [optional] [default to False]
**embedding_options** | [**EmbeddingOptions**](EmbeddingOptions.md) | Embedding output format options | [optional] 
**expires_at** | **datetime** |  | [optional] 

## Example

```python
from encypher.models.sign_options import SignOptions

# TODO update the JSON string below
json = "{}"
# create an instance of SignOptions from a JSON string
sign_options_instance = SignOptions.from_json(json)
# print the JSON string representation of the object
print(SignOptions.to_json())

# convert the object into a dict
sign_options_dict = sign_options_instance.to_dict()
# create an instance of SignOptions from a dict
sign_options_from_dict = SignOptions.from_dict(sign_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


