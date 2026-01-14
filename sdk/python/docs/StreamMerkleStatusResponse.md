# StreamMerkleStatusResponse

Response with streaming Merkle session status.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether status check was successful | 
**session_id** | **str** | Session identifier | 
**document_id** | **str** | Document identifier | 
**status** | **str** | Session status: active, finalized, expired | 
**total_segments** | **int** | Total segments added | 
**buffer_count** | **int** | Segments currently in buffer | 
**intermediate_root** | **str** |  | [optional] 
**created_at** | **datetime** | When session was created | 
**expires_at** | **datetime** | When session will expire | 
**last_activity** | **datetime** | Last activity timestamp | 

## Example

```python
from encypher.models.stream_merkle_status_response import StreamMerkleStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StreamMerkleStatusResponse from a JSON string
stream_merkle_status_response_instance = StreamMerkleStatusResponse.from_json(json)
# print the JSON string representation of the object
print(StreamMerkleStatusResponse.to_json())

# convert the object into a dict
stream_merkle_status_response_dict = stream_merkle_status_response_instance.to_dict()
# create an instance of StreamMerkleStatusResponse from a dict
stream_merkle_status_response_from_dict = StreamMerkleStatusResponse.from_dict(stream_merkle_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


