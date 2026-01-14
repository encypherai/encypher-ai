# StreamMerkleStatusRequest

Request to check status of a streaming Merkle session.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **str** | Session ID to check | 

## Example

```python
from encypher.models.stream_merkle_status_request import StreamMerkleStatusRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StreamMerkleStatusRequest from a JSON string
stream_merkle_status_request_instance = StreamMerkleStatusRequest.from_json(json)
# print the JSON string representation of the object
print(StreamMerkleStatusRequest.to_json())

# convert the object into a dict
stream_merkle_status_request_dict = stream_merkle_status_request_instance.to_dict()
# create an instance of StreamMerkleStatusRequest from a dict
stream_merkle_status_request_from_dict = StreamMerkleStatusRequest.from_dict(stream_merkle_status_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


