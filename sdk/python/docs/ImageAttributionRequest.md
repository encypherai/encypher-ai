# ImageAttributionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**image_data** | **str** |  | [optional]
**phash** | **str** |  | [optional]
**threshold** | **int** | Max Hamming distance (0&#x3D;exact, 10&#x3D;default, 32&#x3D;very loose) | [optional] [default to 10]
**scope** | **str** | &#39;org&#39; &#x3D; search within your organization (all tiers). &#39;all&#39; &#x3D; cross-organization search (Enterprise only). | [optional] [default to 'org']

## Example

```python
from encypher.models.image_attribution_request import ImageAttributionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAttributionRequest from a JSON string
image_attribution_request_instance = ImageAttributionRequest.from_json(json)
# print the JSON string representation of the object
print(ImageAttributionRequest.to_json())

# convert the object into a dict
image_attribution_request_dict = image_attribution_request_instance.to_dict()
# create an instance of ImageAttributionRequest from a dict
image_attribution_request_from_dict = ImageAttributionRequest.from_dict(image_attribution_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
