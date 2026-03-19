# GhostTokenRegenerateResponse

Response after regenerating the webhook token.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**webhook_url** | **str** | New webhook URL with the regenerated token. Update this in Ghost. |
**webhook_token** | **str** | New webhook token (ghwh_...). Store it now — it won&#39;t be shown again. |

## Example

```python
from encypher.models.ghost_token_regenerate_response import GhostTokenRegenerateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GhostTokenRegenerateResponse from a JSON string
ghost_token_regenerate_response_instance = GhostTokenRegenerateResponse.from_json(json)
# print the JSON string representation of the object
print(GhostTokenRegenerateResponse.to_json())

# convert the object into a dict
ghost_token_regenerate_response_dict = ghost_token_regenerate_response_instance.to_dict()
# create an instance of GhostTokenRegenerateResponse from a dict
ghost_token_regenerate_response_from_dict = GhostTokenRegenerateResponse.from_dict(ghost_token_regenerate_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
