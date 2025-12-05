# ChatCompletionRequest

OpenAI-compatible chat completion request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**messages** | [**List[ChatMessage]**](ChatMessage.md) |  | 
**model** | **str** |  | [optional] 
**temperature** | **float** |  | [optional] 
**top_p** | **float** |  | [optional] 
**n** | **int** |  | [optional] 
**stream** | **bool** |  | [optional] [default to False]
**stop** | **List[str]** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**presence_penalty** | **float** |  | [optional] 
**frequency_penalty** | **float** |  | [optional] 
**user** | **str** |  | [optional] 
**sign_response** | **bool** |  | [optional] [default to True]

## Example

```python
from encypher.models.chat_completion_request import ChatCompletionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ChatCompletionRequest from a JSON string
chat_completion_request_instance = ChatCompletionRequest.from_json(json)
# print the JSON string representation of the object
print(ChatCompletionRequest.to_json())

# convert the object into a dict
chat_completion_request_dict = chat_completion_request_instance.to_dict()
# create an instance of ChatCompletionRequest from a dict
chat_completion_request_from_dict = ChatCompletionRequest.from_dict(chat_completion_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


