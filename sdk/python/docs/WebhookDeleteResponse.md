# WebhookDeleteResponse

Response after deleting a webhook.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 

## Example

```python
from encypher.models.webhook_delete_response import WebhookDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookDeleteResponse from a JSON string
webhook_delete_response_instance = WebhookDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(WebhookDeleteResponse.to_json())

# convert the object into a dict
webhook_delete_response_dict = webhook_delete_response_instance.to_dict()
# create an instance of WebhookDeleteResponse from a dict
webhook_delete_response_from_dict = WebhookDeleteResponse.from_dict(webhook_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


