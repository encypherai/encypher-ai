# CdnVariantsResponse

Response for POST /cdn/images/{record_id}/variants.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parent_record_id** | **str** |  |
**variant_count** | **int** |  |
**variant_ids** | **List[str]** |  |

## Example

```python
from encypher.models.cdn_variants_response import CdnVariantsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CdnVariantsResponse from a JSON string
cdn_variants_response_instance = CdnVariantsResponse.from_json(json)
# print the JSON string representation of the object
print(CdnVariantsResponse.to_json())

# convert the object into a dict
cdn_variants_response_dict = cdn_variants_response_instance.to_dict()
# create an instance of CdnVariantsResponse from a dict
cdn_variants_response_from_dict = CdnVariantsResponse.from_dict(cdn_variants_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
