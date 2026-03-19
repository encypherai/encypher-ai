# ImageVerifyResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**valid** | **bool** |  |
**verified_at** | **str** |  |
**c2pa_manifest** | **Dict[str, object]** |  | [optional]
**image_id** | **str** |  | [optional]
**document_id** | **str** |  | [optional]
**hash** | **str** |  | [optional]
**phash** | **str** |  | [optional]
**cryptographically_verified** | **bool** |  | [optional]
**db_matched** | **bool** |  | [optional]
**historically_signed_by_us** | **bool** |  | [optional]
**overall_status** | **str** |  | [optional]
**error** | **str** |  | [optional]
**correlation_id** | **str** |  |

## Example

```python
from encypher.models.image_verify_response import ImageVerifyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ImageVerifyResponse from a JSON string
image_verify_response_instance = ImageVerifyResponse.from_json(json)
# print the JSON string representation of the object
print(ImageVerifyResponse.to_json())

# convert the object into a dict
image_verify_response_dict = image_verify_response_instance.to_dict()
# create an instance of ImageVerifyResponse from a dict
image_verify_response_from_dict = ImageVerifyResponse.from_dict(image_verify_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
