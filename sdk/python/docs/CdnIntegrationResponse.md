# CdnIntegrationResponse

Response schema for CDN integration config.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  |
**provider** | **str** |  |
**zone_id** | **str** |  |
**enabled** | **bool** |  |
**created_at** | **datetime** |  |
**updated_at** | **datetime** |  |
**webhook_url** | **str** |  |

## Example

```python
from encypher.models.cdn_integration_response import CdnIntegrationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CdnIntegrationResponse from a JSON string
cdn_integration_response_instance = CdnIntegrationResponse.from_json(json)
# print the JSON string representation of the object
print(CdnIntegrationResponse.to_json())

# convert the object into a dict
cdn_integration_response_dict = cdn_integration_response_instance.to_dict()
# create an instance of CdnIntegrationResponse from a dict
cdn_integration_response_from_dict = CdnIntegrationResponse.from_dict(cdn_integration_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
