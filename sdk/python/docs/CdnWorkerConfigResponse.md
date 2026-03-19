# CdnWorkerConfigResponse

Response for POST /cdn/integrations/{id}/generate-worker-config.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**worker_script** | **str** |  |
**wrangler_toml** | **str** |  |
**integration_id** | **str** |  |

## Example

```python
from encypher.models.cdn_worker_config_response import CdnWorkerConfigResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CdnWorkerConfigResponse from a JSON string
cdn_worker_config_response_instance = CdnWorkerConfigResponse.from_json(json)
# print the JSON string representation of the object
print(CdnWorkerConfigResponse.to_json())

# convert the object into a dict
cdn_worker_config_response_dict = cdn_worker_config_response_instance.to_dict()
# create an instance of CdnWorkerConfigResponse from a dict
cdn_worker_config_response_from_dict = CdnWorkerConfigResponse.from_dict(cdn_worker_config_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
