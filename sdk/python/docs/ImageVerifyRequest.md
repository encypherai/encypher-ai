# ImageVerifyRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**image_data** | **str** |  |
**mime_type** | **str** |  | [optional] [default to 'image/jpeg']

## Example

```python
from encypher.models.image_verify_request import ImageVerifyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ImageVerifyRequest from a JSON string
image_verify_request_instance = ImageVerifyRequest.from_json(json)
# print the JSON string representation of the object
print(ImageVerifyRequest.to_json())

# convert the object into a dict
image_verify_request_dict = image_verify_request_instance.to_dict()
# create an instance of ImageVerifyRequest from a dict
image_verify_request_from_dict = ImageVerifyRequest.from_dict(image_verify_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
