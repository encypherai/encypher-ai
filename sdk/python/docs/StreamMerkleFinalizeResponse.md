# StreamMerkleFinalizeResponse

Response after finalizing a streaming Merkle session.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether finalization was successful | 
**session_id** | **str** | Session identifier | 
**document_id** | **str** | Document identifier | 
**root_hash** | **str** | Final Merkle root hash | 
**tree_depth** | **int** | Depth of the Merkle tree | 
**total_segments** | **int** | Total number of segments in tree | 
**embedded_content** | **str** |  | [optional] 
**instance_id** | **str** |  | [optional] 
**processing_time_ms** | **float** | Total processing time in milliseconds | 
**message** | **str** | Status message | 

## Example

```python
from encypher.models.stream_merkle_finalize_response import StreamMerkleFinalizeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StreamMerkleFinalizeResponse from a JSON string
stream_merkle_finalize_response_instance = StreamMerkleFinalizeResponse.from_json(json)
# print the JSON string representation of the object
print(StreamMerkleFinalizeResponse.to_json())

# convert the object into a dict
stream_merkle_finalize_response_dict = stream_merkle_finalize_response_instance.to_dict()
# create an instance of StreamMerkleFinalizeResponse from a dict
stream_merkle_finalize_response_from_dict = StreamMerkleFinalizeResponse.from_dict(stream_merkle_finalize_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


