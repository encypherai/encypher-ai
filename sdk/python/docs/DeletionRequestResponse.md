# DeletionRequestResponse

Response for a deletion request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  |
**organization_id** | **str** |  |
**requested_by** | **str** |  |
**scope** | **str** |  |
**reason** | **str** |  |
**status** | **str** |  |
**requested_at** | **str** |  |
**scheduled_purge_at** | **str** |  |

## Example

```python
from encypher.models.deletion_request_response import DeletionRequestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeletionRequestResponse from a JSON string
deletion_request_response_instance = DeletionRequestResponse.from_json(json)
# print the JSON string representation of the object
print(DeletionRequestResponse.to_json())

# convert the object into a dict
deletion_request_response_dict = deletion_request_response_instance.to_dict()
# create an instance of DeletionRequestResponse from a dict
deletion_request_response_from_dict = DeletionRequestResponse.from_dict(deletion_request_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
