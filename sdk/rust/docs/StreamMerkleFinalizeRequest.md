# StreamMerkleFinalizeRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **String** | Session ID to finalize | 
**embed_manifest** | Option<**bool**> | Whether to embed C2PA manifest into the final document | [optional][default to true]
**manifest_mode** | Option<**String**> | Manifest mode: full, lightweight_uuid, hybrid | [optional][default to full]
**action** | Option<**String**> | C2PA action type: c2pa.created or c2pa.edited | [optional][default to c2pa.created]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


