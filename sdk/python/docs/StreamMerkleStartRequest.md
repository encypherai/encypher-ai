# StreamMerkleStartRequest

Request to start a streaming Merkle tree construction session.  Patent Reference: FIG. 5 - Streaming Merkle Tree Construction  This initiates a session that allows segments to be added incrementally, ideal for real-time LLM output signing where content is generated token-by-token.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Unique document identifier | 
**segmentation_level** | **str** | Segmentation level: sentence, paragraph, section | [optional] [default to 'sentence']
**metadata** | **Dict[str, object]** |  | [optional] 
**buffer_size** | **int** | Maximum number of segments to buffer before forcing a flush | [optional] [default to 100]
**auto_finalize_timeout_seconds** | **int** | Timeout in seconds after which session auto-finalizes if idle | [optional] [default to 300]

## Example

```python
from encypher.models.stream_merkle_start_request import StreamMerkleStartRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StreamMerkleStartRequest from a JSON string
stream_merkle_start_request_instance = StreamMerkleStartRequest.from_json(json)
# print the JSON string representation of the object
print(StreamMerkleStartRequest.to_json())

# convert the object into a dict
stream_merkle_start_request_dict = stream_merkle_start_request_instance.to_dict()
# create an instance of StreamMerkleStartRequest from a dict
stream_merkle_start_request_from_dict = StreamMerkleStartRequest.from_dict(stream_merkle_start_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


