# DeletionRequestCreate

Request to delete user or organization data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reason** | **str** |  | [optional]
**scope** | **str** | Scope of deletion: &#39;account&#39; (full account) or &#39;personal_data&#39; (PII only) | [optional] [default to 'account']
**confirm** | **bool** | Must be true to confirm the deletion request |

## Example

```python
from encypher.models.deletion_request_create import DeletionRequestCreate

# TODO update the JSON string below
json = "{}"
# create an instance of DeletionRequestCreate from a JSON string
deletion_request_create_instance = DeletionRequestCreate.from_json(json)
# print the JSON string representation of the object
print(DeletionRequestCreate.to_json())

# convert the object into a dict
deletion_request_create_dict = deletion_request_create_instance.to_dict()
# create an instance of DeletionRequestCreate from a dict
deletion_request_create_from_dict = DeletionRequestCreate.from_dict(deletion_request_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
