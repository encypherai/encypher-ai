# AdminPurgeResponse

Response for an admin purge operation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**request_id** | **str** |  |
**user_email** | **str** |  |
**status** | **str** |  |
**scheduled_purge_at** | **str** |  |
**records_marked** | **int** |  |

## Example

```python
from encypher.models.admin_purge_response import AdminPurgeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AdminPurgeResponse from a JSON string
admin_purge_response_instance = AdminPurgeResponse.from_json(json)
# print the JSON string representation of the object
print(AdminPurgeResponse.to_json())

# convert the object into a dict
admin_purge_response_dict = admin_purge_response_instance.to_dict()
# create an instance of AdminPurgeResponse from a dict
admin_purge_response_from_dict = AdminPurgeResponse.from_dict(admin_purge_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
