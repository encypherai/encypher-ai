# WebhookCreateResponse

Response after creating a webhook.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 

## Example

```python
from encypher.models.webhook_create_response import WebhookCreateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookCreateResponse from a JSON string
webhook_create_response_instance = WebhookCreateResponse.from_json(json)
# print the JSON string representation of the object
print(WebhookCreateResponse.to_json())

# convert the object into a dict
webhook_create_response_dict = webhook_create_response_instance.to_dict()
# create an instance of WebhookCreateResponse from a dict
webhook_create_response_from_dict = WebhookCreateResponse.from_dict(webhook_create_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


