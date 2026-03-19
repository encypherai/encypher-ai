# CdnImageSignResponse

Response for POST /cdn/images/sign.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**record_id** | **str** |  |
**manifest_url** | **str** |  |
**image_id** | **str** |  |
**phash** | **int** |  | [optional]
**sha256** | **str** |  | [optional]
**signed_image_b64** | **str** |  |
**mime_type** | **str** |  |

## Example

```python
from encypher.models.cdn_image_sign_response import CdnImageSignResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CdnImageSignResponse from a JSON string
cdn_image_sign_response_instance = CdnImageSignResponse.from_json(json)
# print the JSON string representation of the object
print(CdnImageSignResponse.to_json())

# convert the object into a dict
cdn_image_sign_response_dict = cdn_image_sign_response_instance.to_dict()
# create an instance of CdnImageSignResponse from a dict
cdn_image_sign_response_from_dict = CdnImageSignResponse.from_dict(cdn_image_sign_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
