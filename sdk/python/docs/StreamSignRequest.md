# StreamSignRequest

Request payload for streaming signing run.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Content to sign while streaming progress | 
**document_id** | **str** |  | [optional] 
**document_title** | **str** |  | [optional] 
**document_type** | **str** | Document type metadata | [optional] [default to 'article']
**run_id** | **str** |  | [optional] 

## Example

```python
from encypher.models.stream_sign_request import StreamSignRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StreamSignRequest from a JSON string
stream_sign_request_instance = StreamSignRequest.from_json(json)
# print the JSON string representation of the object
print(StreamSignRequest.to_json())

# convert the object into a dict
stream_sign_request_dict = stream_sign_request_instance.to_dict()
# create an instance of StreamSignRequest from a dict
stream_sign_request_from_dict = StreamSignRequest.from_dict(stream_sign_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


