# ImageAttributionMatchResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**image_id** | **str** |  |
**document_id** | **str** |  |
**organization_id** | **str** |  |
**filename** | **str** |  |
**hamming_distance** | **int** |  |
**similarity_score** | **float** |  |
**signed_hash** | **str** |  |
**created_at** | **str** |  |

## Example

```python
from encypher.models.image_attribution_match_response import ImageAttributionMatchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAttributionMatchResponse from a JSON string
image_attribution_match_response_instance = ImageAttributionMatchResponse.from_json(json)
# print the JSON string representation of the object
print(ImageAttributionMatchResponse.to_json())

# convert the object into a dict
image_attribution_match_response_dict = image_attribution_match_response_instance.to_dict()
# create an instance of ImageAttributionMatchResponse from a dict
image_attribution_match_response_from_dict = ImageAttributionMatchResponse.from_dict(image_attribution_match_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
