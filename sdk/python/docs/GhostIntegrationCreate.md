# GhostIntegrationCreate

Request body for creating/updating a Ghost integration.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ghost_url** | **str** | URL of the Ghost instance (e.g. https://myblog.ghost.io) |
**ghost_admin_api_key** | **str** | Ghost Admin API key (format: {id}:{secret}) |
**auto_sign_on_publish** | **bool** | Automatically sign posts when published | [optional] [default to True]
**auto_sign_on_update** | **bool** | Automatically re-sign posts when updated | [optional] [default to True]
**manifest_mode** | **str** | C2PA manifest mode for signing | [optional] [default to 'micro']
**segmentation_level** | **str** | Text segmentation level for signing | [optional] [default to 'sentence']
**ecc** | **bool** | Enable Reed-Solomon error correction for micro mode markers. | [optional] [default to True]
**embed_c2pa** | **bool** | Embed full C2PA manifest into content when using micro mode. | [optional] [default to True]
**badge_enabled** | **bool** | Inject verification badge into posts | [optional] [default to True]

## Example

```python
from encypher.models.ghost_integration_create import GhostIntegrationCreate

# TODO update the JSON string below
json = "{}"
# create an instance of GhostIntegrationCreate from a JSON string
ghost_integration_create_instance = GhostIntegrationCreate.from_json(json)
# print the JSON string representation of the object
print(GhostIntegrationCreate.to_json())

# convert the object into a dict
ghost_integration_create_dict = ghost_integration_create_instance.to_dict()
# create an instance of GhostIntegrationCreate from a dict
ghost_integration_create_from_dict = GhostIntegrationCreate.from_dict(ghost_integration_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
