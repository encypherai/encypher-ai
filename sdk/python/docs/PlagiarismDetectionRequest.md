# PlagiarismDetectionRequest

Request schema for plagiarism detection.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**target_text** | **str** | Text to check for plagiarism | 
**target_document_id** | **str** |  | [optional] 
**segmentation_level** | **str** | Segmentation level to analyze | [optional] [default to 'sentence']
**include_heat_map** | **bool** | Whether to generate heat map visualization data | [optional] [default to True]
**min_match_percentage** | **float** | Minimum match percentage to include in results | [optional] [default to 0.0]

## Example

```python
from encypher.models.plagiarism_detection_request import PlagiarismDetectionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PlagiarismDetectionRequest from a JSON string
plagiarism_detection_request_instance = PlagiarismDetectionRequest.from_json(json)
# print the JSON string representation of the object
print(PlagiarismDetectionRequest.to_json())

# convert the object into a dict
plagiarism_detection_request_dict = plagiarism_detection_request_instance.to_dict()
# create an instance of PlagiarismDetectionRequest from a dict
plagiarism_detection_request_from_dict = PlagiarismDetectionRequest.from_dict(plagiarism_detection_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


