# SourceAttributionRequest

Request schema for finding source documents.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text_segment** | **str** | Text segment to search for | 
**segmentation_level** | **str** | Segmentation level to search at | [optional] [default to 'sentence']
**normalize** | **bool** | Whether to normalize text before hashing | [optional] [default to True]
**include_proof** | **bool** | Whether to include Merkle proof in response | [optional] [default to False]

## Example

```python
from encypher.models.source_attribution_request import SourceAttributionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SourceAttributionRequest from a JSON string
source_attribution_request_instance = SourceAttributionRequest.from_json(json)
# print the JSON string representation of the object
print(SourceAttributionRequest.to_json())

# convert the object into a dict
source_attribution_request_dict = source_attribution_request_instance.to_dict()
# create an instance of SourceAttributionRequest from a dict
source_attribution_request_from_dict = SourceAttributionRequest.from_dict(source_attribution_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


