# WebhookUpdateRequest

Request to update a webhook.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** |  | [optional] 
**events** | **List[str]** |  | [optional] 
**is_active** | **bool** |  | [optional] 

## Example

```python
from encypher.models.webhook_update_request import WebhookUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookUpdateRequest from a JSON string
webhook_update_request_instance = WebhookUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(WebhookUpdateRequest.to_json())

# convert the object into a dict
webhook_update_request_dict = webhook_update_request_instance.to_dict()
# create an instance of WebhookUpdateRequest from a dict
webhook_update_request_from_dict = WebhookUpdateRequest.from_dict(webhook_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


