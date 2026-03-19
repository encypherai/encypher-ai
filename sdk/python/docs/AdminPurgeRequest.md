# AdminPurgeRequest

Admin request to purge a specific user's data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_email** | **str** | Email of the user whose data to purge |
**reason** | **str** | Administrative reason for purge |
**confirm** | **bool** | Must be true to confirm the purge |

## Example

```python
from encypher.models.admin_purge_request import AdminPurgeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AdminPurgeRequest from a JSON string
admin_purge_request_instance = AdminPurgeRequest.from_json(json)
# print the JSON string representation of the object
print(AdminPurgeRequest.to_json())

# convert the object into a dict
admin_purge_request_dict = admin_purge_request_instance.to_dict()
# create an instance of AdminPurgeRequest from a dict
admin_purge_request_from_dict = AdminPurgeRequest.from_dict(admin_purge_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
