# PlagiarismDetectionResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**report_id** | [**uuid::Uuid**](uuid::Uuid.md) |  | 
**target_document_id** | Option<**String**> |  | 
**total_segments** | **i32** |  | 
**matched_segments** | **i32** |  | 
**overall_match_percentage** | **f64** |  | 
**source_documents** | [**Vec<models::SourceDocumentMatch>**](SourceDocumentMatch.md) |  | 
**heat_map_data** | Option<[**models::HeatMapData**](HeatMapData.md)> |  | 
**processing_time_ms** | **f64** |  | 
**scan_timestamp** | **String** |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


