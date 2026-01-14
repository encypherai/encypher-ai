# StreamMerkleSegmentResponse

Response after adding a segment to the streaming Merkle tree.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether segment was added successfully | 
**session_id** | **str** | Session identifier | 
**segment_index** | **int** | Index of the added segment | 
**segment_hash** | **str** | SHA-256 hash of the segment | 
**buffer_count** | **int** | Current number of segments in buffer | 
**total_segments** | **int** | Total segments added to session | 
**intermediate_root** | **str** |  | [optional] 
**message** | **str** | Status message | 

## Example

```python
from encypher.models.stream_merkle_segment_response import StreamMerkleSegmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StreamMerkleSegmentResponse from a JSON string
stream_merkle_segment_response_instance = StreamMerkleSegmentResponse.from_json(json)
# print the JSON string representation of the object
print(StreamMerkleSegmentResponse.to_json())

# convert the object into a dict
stream_merkle_segment_response_dict = stream_merkle_segment_response_instance.to_dict()
# create an instance of StreamMerkleSegmentResponse from a dict
stream_merkle_segment_response_from_dict = StreamMerkleSegmentResponse.from_dict(stream_merkle_segment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


