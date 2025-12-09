# PendingInvite

Pending team invitation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**email** | **str** |  | 
**role** | **str** |  | 
**invited_by** | **str** |  | 
**status** | **str** |  | 
**expires_at** | **str** |  | 
**created_at** | **str** |  | 

## Example

```python
from encypher.models.pending_invite import PendingInvite

# TODO update the JSON string below
json = "{}"
# create an instance of PendingInvite from a JSON string
pending_invite_instance = PendingInvite.from_json(json)
# print the JSON string representation of the object
print(PendingInvite.to_json())

# convert the object into a dict
pending_invite_dict = pending_invite_instance.to_dict()
# create an instance of PendingInvite from a dict
pending_invite_from_dict = PendingInvite.from_dict(pending_invite_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


