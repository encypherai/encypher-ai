# GhostIntegrationResponse

Response for Ghost integration config (key masked).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  |
**organization_id** | **str** |  |
**ghost_url** | **str** |  |
**ghost_admin_api_key_masked** | **str** | Masked Admin API key (only last 4 chars visible) |
**auto_sign_on_publish** | **bool** |  |
**auto_sign_on_update** | **bool** |  |
**manifest_mode** | **str** |  |
**segmentation_level** | **str** |  |
**ecc** | **bool** |  |
**embed_c2pa** | **bool** |  |
**badge_enabled** | **bool** |  |
**is_active** | **bool** |  |
**webhook_url** | **str** | The ready-to-paste URL to configure in Ghost webhooks. Contains a scoped token (not your API key). |
**webhook_token** | **str** |  | [optional]
**last_webhook_at** | **datetime** |  | [optional]
**last_sign_at** | **datetime** |  | [optional]
**sign_count** | **str** |  | [optional] [default to '0']
**created_at** | **datetime** |  | [optional]
**updated_at** | **datetime** |  | [optional]

## Example

```python
from encypher.models.ghost_integration_response import GhostIntegrationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GhostIntegrationResponse from a JSON string
ghost_integration_response_instance = GhostIntegrationResponse.from_json(json)
# print the JSON string representation of the object
print(GhostIntegrationResponse.to_json())

# convert the object into a dict
ghost_integration_response_dict = ghost_integration_response_instance.to_dict()
# create an instance of GhostIntegrationResponse from a dict
ghost_integration_response_from_dict = GhostIntegrationResponse.from_dict(ghost_integration_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
