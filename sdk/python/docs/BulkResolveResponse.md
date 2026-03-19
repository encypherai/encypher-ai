# BulkResolveResponse

Response for bulk UUID resolution.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | [**List[ZWResolveResponse]**](ZWResolveResponse.md) |  | [optional]
**not_found** | **List[str]** |  | [optional]

## Example

```python
from encypher.models.bulk_resolve_response import BulkResolveResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkResolveResponse from a JSON string
bulk_resolve_response_instance = BulkResolveResponse.from_json(json)
# print the JSON string representation of the object
print(BulkResolveResponse.to_json())

# convert the object into a dict
bulk_resolve_response_dict = bulk_resolve_response_instance.to_dict()
# create an instance of BulkResolveResponse from a dict
bulk_resolve_response_from_dict = BulkResolveResponse.from_dict(bulk_resolve_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
