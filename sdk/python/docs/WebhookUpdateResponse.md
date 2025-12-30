# WebhookUpdateResponse

Response after updating a webhook.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 

## Example

```python
from encypher.models.webhook_update_response import WebhookUpdateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookUpdateResponse from a JSON string
webhook_update_response_instance = WebhookUpdateResponse.from_json(json)
# print the JSON string representation of the object
print(WebhookUpdateResponse.to_json())

# convert the object into a dict
webhook_update_response_dict = webhook_update_response_instance.to_dict()
# create an instance of WebhookUpdateResponse from a dict
webhook_update_response_from_dict = WebhookUpdateResponse.from_dict(webhook_update_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


