# PlagiarismDetectionRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**target_text** | **String** | Text to check for plagiarism | 
**target_document_id** | Option<**String**> |  | [optional]
**segmentation_level** | Option<**String**> | Segmentation level to analyze | [optional][default to sentence]
**include_heat_map** | Option<**bool**> | Whether to generate heat map visualization data | [optional][default to true]
**min_match_percentage** | Option<**f64**> | Minimum match percentage to include in results | [optional][default to 0.0]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


