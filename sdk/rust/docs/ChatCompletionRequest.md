# ChatCompletionRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**messages** | [**Vec<models::ChatMessage>**](ChatMessage.md) |  | 
**model** | Option<**String**> |  | [optional]
**temperature** | Option<**f64**> |  | [optional]
**top_p** | Option<**f64**> |  | [optional]
**n** | Option<**i32**> |  | [optional]
**stream** | Option<**bool**> |  | [optional][default to false]
**stop** | Option<**Vec<String>**> |  | [optional]
**max_tokens** | Option<**i32**> |  | [optional]
**presence_penalty** | Option<**f64**> |  | [optional]
**frequency_penalty** | Option<**f64**> |  | [optional]
**user** | Option<**String**> |  | [optional]
**sign_response** | Option<**bool**> |  | [optional][default to true]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


