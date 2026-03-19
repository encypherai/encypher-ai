# CdnVariantsRequest

Request body for POST /cdn/images/{record_id}/variants.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**transforms** | **List[str]** |  |

## Example

```python
from encypher.models.cdn_variants_request import CdnVariantsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CdnVariantsRequest from a JSON string
cdn_variants_request_instance = CdnVariantsRequest.from_json(json)
# print the JSON string representation of the object
print(CdnVariantsRequest.to_json())

# convert the object into a dict
cdn_variants_request_dict = cdn_variants_request_instance.to_dict()
# create an instance of CdnVariantsRequest from a dict
cdn_variants_request_from_dict = CdnVariantsRequest.from_dict(cdn_variants_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
