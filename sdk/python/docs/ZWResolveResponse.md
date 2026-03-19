# ZWResolveResponse

Response for ZW segment UUID resolution.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**segment_uuid** | **str** |  |
**organization_id** | **str** |  |
**document_id** | **str** |  | [optional]
**manifest_mode** | **str** |  | [optional]
**segment_location** | [**SegmentLocationResponse**](SegmentLocationResponse.md) |  | [optional]
**total_segments** | **int** |  | [optional]
**leaf_index** | **int** |  | [optional]
**manifest_data** | **Dict[str, object]** |  | [optional]
**rights_resolution_url** | **str** |  | [optional]

## Example

```python
from encypher.models.zw_resolve_response import ZWResolveResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ZWResolveResponse from a JSON string
zw_resolve_response_instance = ZWResolveResponse.from_json(json)
# print the JSON string representation of the object
print(ZWResolveResponse.to_json())

# convert the object into a dict
zw_resolve_response_dict = zw_resolve_response_instance.to_dict()
# create an instance of ZWResolveResponse from a dict
zw_resolve_response_from_dict = ZWResolveResponse.from_dict(zw_resolve_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
