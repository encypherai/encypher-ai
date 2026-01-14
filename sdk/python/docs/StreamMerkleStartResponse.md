# StreamMerkleStartResponse

Response after starting a streaming Merkle session.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether session was created successfully | 
**session_id** | **str** | Unique session identifier for subsequent calls | 
**document_id** | **str** | Document identifier | 
**expires_at** | **datetime** | When the session will expire if idle | 
**buffer_size** | **int** | Maximum buffer size before auto-flush | 
**message** | **str** | Status message | 

## Example

```python
from encypher.models.stream_merkle_start_response import StreamMerkleStartResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StreamMerkleStartResponse from a JSON string
stream_merkle_start_response_instance = StreamMerkleStartResponse.from_json(json)
# print the JSON string representation of the object
print(StreamMerkleStartResponse.to_json())

# convert the object into a dict
stream_merkle_start_response_dict = stream_merkle_start_response_instance.to_dict()
# create an instance of StreamMerkleStartResponse from a dict
stream_merkle_start_response_from_dict = StreamMerkleStartResponse.from_dict(stream_merkle_start_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


