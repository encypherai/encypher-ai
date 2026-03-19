# SignOptions

Options for signing - features are gated by tier.  Tier Feature Matrix:  | Feature                  | Free | Enterprise | |--------------------------|:----:|:----------:| | document_type            | yes  | yes        | | claim_generator          | yes  | yes        | | segmentation_level       | all except word | all | | manifest_mode            | all  | all        | | embedding_strategy       | all  | all        | | index_for_attribution    | yes  | yes        | | custom_assertions        | yes  | yes        | | template_id              | yes  | yes        | | rights / use_rights_profile | yes | yes     | | add_dual_binding         | no   | yes        | | include_fingerprint      | no   | yes        | | enable_print_fingerprint | no   | yes        | | word segmentation        | no   | yes        | | batch (documents array)  | 10   | 100        |

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_type** | **str** | Document type: article, legal_brief, contract, ai_output | [optional] [default to 'article']
**claim_generator** | **str** |  | [optional]
**action** | **str** | C2PA action type: c2pa.created (new) or c2pa.edited (modified) | [optional] [default to 'c2pa.created']
**previous_instance_id** | **str** |  | [optional]
**digital_source_type** | **str** |  | [optional]
**segmentation_level** | **str** | Segmentation level: document, sentence, paragraph, section (all Free); word (Enterprise only) | [optional] [default to 'document']
**segmentation_levels** | **List[str]** |  | [optional]
**manifest_mode** | **str** | Manifest mode: full or micro. micro uses ultra-compact per-segment markers; behaviour controlled by ecc, embed_c2pa, and legacy_safe flags. | [optional] [default to 'full']
**ecc** | **bool** | Enable Reed-Solomon error correction for micro mode (44 chars/segment vs 36). Ignored for non-micro modes. | [optional] [default to True]
**legacy_safe** | **bool** | Use Word-safe/terminal-safe base-6 encoding for micro mode instead of VS256. ecc&#x3D;False -&gt; 100 chars/segment; ecc&#x3D;True -&gt; 112 chars/segment (RS parity). Ignored for non-micro modes. | [optional] [default to False]
**embed_c2pa** | **bool** | Embed full C2PA document manifest into signed content for micro mode. When false, per-sentence markers only; C2PA manifest is still generated and stored in DB. Ignored for non-micro modes. | [optional] [default to True]
**embedding_strategy** | **str** | Embedding strategy: single_point, distributed, distributed_redundant (all Free) | [optional] [default to 'single_point']
**distribution_target** | **str** |  | [optional]
**index_for_attribution** | **bool** | Index content for attribution and plagiarism detection (Free) | [optional] [default to False]
**custom_assertions** | **List[Dict[str, object]]** |  | [optional]
**template_id** | **str** |  | [optional]
**validate_assertions** | **bool** | Whether to validate custom assertions against registered schemas (Free) | [optional] [default to True]
**rights** | [**RightsMetadata**](RightsMetadata.md) |  | [optional]
**use_rights_profile** | **bool** | When True, fetches the publisher&#39;s active rights profile, stores a snapshot on the content reference, and adds rights_resolution_url to the response (Free) | [optional] [default to False]
**license** | [**LicenseInfo**](LicenseInfo.md) |  | [optional]
**actions** | **List[Dict[str, object]]** |  | [optional]
**add_dual_binding** | **bool** | Enable additional integrity binding (Enterprise) | [optional] [default to False]
**include_fingerprint** | **bool** | Include robust fingerprint that survives modifications (Enterprise) | [optional] [default to False]
**enable_print_fingerprint** | **bool** | Print Leak Detection - embed imperceptible spacing patterns that survive printing and scanning, enabling source identification from physical or PDF copies (Enterprise) | [optional] [default to False]
**disable_c2pa** | **bool** | Opt-out of C2PA embedding for non-micro modes, only basic metadata (Enterprise). For micro mode use embed_c2pa instead. | [optional] [default to False]
**store_c2pa_manifest** | **bool** | Persist generated C2PA manifest in content DB for DB-backed verification. Applies to all modes that generate a manifest. | [optional] [default to True]
**embedding_options** | [**EmbeddingOptions**](EmbeddingOptions.md) | Embedding output format options | [optional]
**return_embedding_plan** | **bool** | When true, include an embedding_plan with index-based marker insertion operations in the response. | [optional] [default to False]
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
