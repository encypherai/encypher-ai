# StreamMerkleSegmentRequest

Request to add a segment to an active streaming Merkle session.  Segments are buffered and combined into the Merkle tree incrementally. The tree is constructed using a bounded buffer approach for memory efficiency.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **str** | Session ID from StreamMerkleStartResponse | 
**segment_text** | **str** | Text segment to add to the tree | 
**segment_index** | **int** |  | [optional] 
**is_final** | **bool** | If true, this is the last segment and session should finalize | [optional] [default to False]
**flush_buffer** | **bool** | If true, flush the current buffer to compute intermediate hashes | [optional] [default to False]

## Example

```python
from encypher.models.stream_merkle_segment_request import StreamMerkleSegmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StreamMerkleSegmentRequest from a JSON string
stream_merkle_segment_request_instance = StreamMerkleSegmentRequest.from_json(json)
# print the JSON string representation of the object
print(StreamMerkleSegmentRequest.to_json())

# convert the object into a dict
stream_merkle_segment_request_dict = stream_merkle_segment_request_instance.to_dict()
# create an instance of StreamMerkleSegmentRequest from a dict
stream_merkle_segment_request_from_dict = StreamMerkleSegmentRequest.from_dict(stream_merkle_segment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


