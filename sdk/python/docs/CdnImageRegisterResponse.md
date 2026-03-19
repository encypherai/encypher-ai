# CdnImageRegisterResponse

Response for POST /cdn/images/register.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**record_id** | **str** |  |
**phash** | **int** |  | [optional]
**sha256** | **str** |  | [optional]

## Example

```python
from encypher.models.cdn_image_register_response import CdnImageRegisterResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CdnImageRegisterResponse from a JSON string
cdn_image_register_response_instance = CdnImageRegisterResponse.from_json(json)
# print the JSON string representation of the object
print(CdnImageRegisterResponse.to_json())

# convert the object into a dict
cdn_image_register_response_dict = cdn_image_register_response_instance.to_dict()
# create an instance of CdnImageRegisterResponse from a dict
cdn_image_register_response_from_dict = CdnImageRegisterResponse.from_dict(cdn_image_register_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
