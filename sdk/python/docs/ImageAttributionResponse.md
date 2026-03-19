# ImageAttributionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**query_phash** | **str** |  |
**match_count** | **int** |  |
**matches** | [**List[ImageAttributionMatchResponse]**](ImageAttributionMatchResponse.md) |  |
**scope** | **str** |  |
**threshold** | **int** |  |

## Example

```python
from encypher.models.image_attribution_response import ImageAttributionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAttributionResponse from a JSON string
image_attribution_response_instance = ImageAttributionResponse.from_json(json)
# print the JSON string representation of the object
print(ImageAttributionResponse.to_json())

# convert the object into a dict
image_attribution_response_dict = image_attribution_response_instance.to_dict()
# create an instance of ImageAttributionResponse from a dict
image_attribution_response_from_dict = ImageAttributionResponse.from_dict(image_attribution_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
