# DeletionConfirmResponse

Response for confirming/executing a deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**request_id** | **str** |  |
**status** | **str** |  |
**message** | **str** |  |

## Example

```python
from encypher.models.deletion_confirm_response import DeletionConfirmResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeletionConfirmResponse from a JSON string
deletion_confirm_response_instance = DeletionConfirmResponse.from_json(json)
# print the JSON string representation of the object
print(DeletionConfirmResponse.to_json())

# convert the object into a dict
deletion_confirm_response_dict = deletion_confirm_response_instance.to_dict()
# create an instance of DeletionConfirmResponse from a dict
deletion_confirm_response_from_dict = DeletionConfirmResponse.from_dict(deletion_confirm_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
