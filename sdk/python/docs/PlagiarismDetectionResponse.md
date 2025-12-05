# PlagiarismDetectionResponse

Response schema for plagiarism detection.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**report_id** | **str** |  | 
**target_document_id** | **str** |  | 
**total_segments** | **int** |  | 
**matched_segments** | **int** |  | 
**overall_match_percentage** | **float** |  | 
**source_documents** | [**List[SourceDocumentMatch]**](SourceDocumentMatch.md) |  | 
**heat_map_data** | [**HeatMapData**](HeatMapData.md) |  | 
**processing_time_ms** | **float** |  | 
**scan_timestamp** | **datetime** |  | 

## Example

```python
from encypher.models.plagiarism_detection_response import PlagiarismDetectionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PlagiarismDetectionResponse from a JSON string
plagiarism_detection_response_instance = PlagiarismDetectionResponse.from_json(json)
# print the JSON string representation of the object
print(PlagiarismDetectionResponse.to_json())

# convert the object into a dict
plagiarism_detection_response_dict = plagiarism_detection_response_instance.to_dict()
# create an instance of PlagiarismDetectionResponse from a dict
plagiarism_detection_response_from_dict = PlagiarismDetectionResponse.from_dict(plagiarism_detection_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


