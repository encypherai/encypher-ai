# StreamMerkleFinalizeResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether finalization was successful | 
**session_id** | **String** | Session identifier | 
**document_id** | **String** | Document identifier | 
**root_hash** | **String** | Final Merkle root hash | 
**tree_depth** | **i32** | Depth of the Merkle tree | 
**total_segments** | **i32** | Total number of segments in tree | 
**embedded_content** | Option<**String**> |  | [optional]
**instance_id** | Option<**String**> |  | [optional]
**processing_time_ms** | **f64** | Total processing time in milliseconds | 
**message** | **String** | Status message | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


