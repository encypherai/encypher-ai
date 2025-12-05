# AuditLogResponse

Paginated audit log response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **str** |  | 
**logs** | [**List[AuditLogEntry]**](AuditLogEntry.md) |  | 
**total** | **int** |  | 
**page** | **int** |  | 
**page_size** | **int** |  | 
**has_more** | **bool** |  | 

## Example

```python
from encypher.models.audit_log_response import AuditLogResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AuditLogResponse from a JSON string
audit_log_response_instance = AuditLogResponse.from_json(json)
# print the JSON string representation of the object
print(AuditLogResponse.to_json())

# convert the object into a dict
audit_log_response_dict = audit_log_response_instance.to_dict()
# create an instance of AuditLogResponse from a dict
audit_log_response_from_dict = AuditLogResponse.from_dict(audit_log_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


