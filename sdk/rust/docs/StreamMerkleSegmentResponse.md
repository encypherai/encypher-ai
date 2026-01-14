# StreamMerkleSegmentResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether segment was added successfully | 
**session_id** | **String** | Session identifier | 
**segment_index** | **i32** | Index of the added segment | 
**segment_hash** | **String** | SHA-256 hash of the segment | 
**buffer_count** | **i32** | Current number of segments in buffer | 
**total_segments** | **i32** | Total segments added to session | 
**intermediate_root** | Option<**String**> |  | [optional]
**message** | **String** | Status message | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


