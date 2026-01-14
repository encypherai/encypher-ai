# StreamMerkleSegmentRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **String** | Session ID from StreamMerkleStartResponse | 
**segment_text** | **String** | Text segment to add to the tree | 
**segment_index** | Option<**i32**> |  | [optional]
**is_final** | Option<**bool**> | If true, this is the last segment and session should finalize | [optional][default to false]
**flush_buffer** | Option<**bool**> | If true, flush the current buffer to compute intermediate hashes | [optional][default to false]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


