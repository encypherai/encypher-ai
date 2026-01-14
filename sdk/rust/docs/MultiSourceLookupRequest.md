# MultiSourceLookupRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text_segment** | **String** | Text segment to search for | 
**include_all_sources** | Option<**bool**> | Return all matching sources (not just first) | [optional][default to true]
**order_by** | Option<**String**> | Ordering: chronological (earliest first), authority, or confidence | [optional][default to chronological]
**include_authority_score** | Option<**bool**> | Include authority ranking scores (Enterprise feature) | [optional][default to false]
**max_results** | Option<**i32**> | Maximum number of sources to return | [optional][default to 10]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


