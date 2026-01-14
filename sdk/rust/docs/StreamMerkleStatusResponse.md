# StreamMerkleStatusResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether status check was successful | 
**session_id** | **String** | Session identifier | 
**document_id** | **String** | Document identifier | 
**status** | **String** | Session status: active, finalized, expired | 
**total_segments** | **i32** | Total segments added | 
**buffer_count** | **i32** | Segments currently in buffer | 
**intermediate_root** | Option<**String**> |  | [optional]
**created_at** | **String** | When session was created | 
**expires_at** | **String** | When session will expire | 
**last_activity** | **String** | Last activity timestamp | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


