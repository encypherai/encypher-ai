# BulkResolveRequest

Request body for bulk UUID resolution.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**segment_uuids** | **List[str]** | List of segment UUIDs to resolve |

## Example

```python
from encypher.models.bulk_resolve_request import BulkResolveRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkResolveRequest from a JSON string
bulk_resolve_request_instance = BulkResolveRequest.from_json(json)
# print the JSON string representation of the object
print(BulkResolveRequest.to_json())

# convert the object into a dict
bulk_resolve_request_dict = bulk_resolve_request_instance.to_dict()
# create an instance of BulkResolveRequest from a dict
bulk_resolve_request_from_dict = BulkResolveRequest.from_dict(bulk_resolve_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
