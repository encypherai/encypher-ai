# AuditLogEntry

Single audit log entry.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**timestamp** | **str** |  | 
**action** | **str** |  | 
**actor_id** | **str** |  | 
**actor_type** | **str** |  | 
**resource_type** | **str** |  | 
**resource_id** | **str** |  | [optional] 
**details** | **Dict[str, object]** |  | [optional] 
**ip_address** | **str** |  | [optional] 
**user_agent** | **str** |  | [optional] 

## Example

```python
from encypher.models.audit_log_entry import AuditLogEntry

# TODO update the JSON string below
json = "{}"
# create an instance of AuditLogEntry from a JSON string
audit_log_entry_instance = AuditLogEntry.from_json(json)
# print the JSON string representation of the object
print(AuditLogEntry.to_json())

# convert the object into a dict
audit_log_entry_dict = audit_log_entry_instance.to_dict()
# create an instance of AuditLogEntry from a dict
audit_log_entry_from_dict = AuditLogEntry.from_dict(audit_log_entry_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


