# DeletionRequestListResponse

List of deletion requests.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**requests** | [**List[DeletionRequestResponse]**](DeletionRequestResponse.md) |  |
**total** | **int** |  |

## Example

```python
from encypher.models.deletion_request_list_response import DeletionRequestListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeletionRequestListResponse from a JSON string
deletion_request_list_response_instance = DeletionRequestListResponse.from_json(json)
# print the JSON string representation of the object
print(DeletionRequestListResponse.to_json())

# convert the object into a dict
deletion_request_list_response_dict = deletion_request_list_response_instance.to_dict()
# create an instance of DeletionRequestListResponse from a dict
deletion_request_list_response_from_dict = DeletionRequestListResponse.from_dict(deletion_request_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
