# AppSchemasBatchBatchVerifyRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mode** | **String** | Processing mode: 'c2pa' or 'embeddings' | 
**segmentation_level** | Option<**String**> |  | [optional]
**idempotency_key** | **String** | Caller-supplied key used to deduplicate retries | 
**items** | [**Vec<models::BatchItemPayload>**](BatchItemPayload.md) | Documents to process (max 100) | 
**fail_fast** | Option<**bool**> | Abort remaining items upon the first error when set to true | [optional][default to false]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


