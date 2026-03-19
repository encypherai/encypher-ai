# CdnIntegrationCreate

Request body for creating or updating a CDN integration.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**provider** | **str** | CDN provider slug (cloudflare | fastly | cloudfront) | [optional] [default to 'cloudflare']
**zone_id** | **str** |  | [optional]
**webhook_secret** | **str** | Shared secret to authenticate Logpush requests (stored hashed) |
**enabled** | **bool** |  | [optional] [default to True]

## Example

```python
from encypher.models.cdn_integration_create import CdnIntegrationCreate

# TODO update the JSON string below
json = "{}"
# create an instance of CdnIntegrationCreate from a JSON string
cdn_integration_create_instance = CdnIntegrationCreate.from_json(json)
# print the JSON string representation of the object
print(CdnIntegrationCreate.to_json())

# convert the object into a dict
cdn_integration_create_dict = cdn_integration_create_instance.to_dict()
# create an instance of CdnIntegrationCreate from a dict
cdn_integration_create_from_dict = CdnIntegrationCreate.from_dict(cdn_integration_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
