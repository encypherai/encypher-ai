# MultiSourceLookupResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether lookup succeeded | 
**query_hash** | **String** | Hash of the queried text | 
**total_sources** | **i32** | Total number of matching sources | 
**sources** | Option<[**Vec<models::SourceRecord>**](SourceRecord.md)> | List of matching sources | [optional]
**original_source** | Option<[**models::SourceRecord**](SourceRecord.md)> |  | [optional]
**has_chain** | **bool** | Whether sources form a linked chain | 
**chain_length** | Option<**i32**> | Length of the source chain | [optional][default to 0]
**processing_time_ms** | **f64** | Processing time in milliseconds | 
**message** | **String** | Status message | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


