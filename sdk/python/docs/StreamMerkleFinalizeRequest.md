# StreamMerkleFinalizeRequest

Request to finalize a streaming Merkle session and compute the final root.  This completes the tree construction, computes the final root hash, and optionally embeds a C2PA manifest into the full document.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **str** | Session ID to finalize | 
**embed_manifest** | **bool** | Whether to embed C2PA manifest into the final document | [optional] [default to True]
**manifest_mode** | **str** | Manifest mode: full, lightweight_uuid, minimal_uuid, hybrid | [optional] [default to 'full']
**action** | **str** | C2PA action type: c2pa.created or c2pa.edited | [optional] [default to 'c2pa.created']

## Example

```python
from encypher.models.stream_merkle_finalize_request import StreamMerkleFinalizeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StreamMerkleFinalizeRequest from a JSON string
stream_merkle_finalize_request_instance = StreamMerkleFinalizeRequest.from_json(json)
# print the JSON string representation of the object
print(StreamMerkleFinalizeRequest.to_json())

# convert the object into a dict
stream_merkle_finalize_request_dict = stream_merkle_finalize_request_instance.to_dict()
# create an instance of StreamMerkleFinalizeRequest from a dict
stream_merkle_finalize_request_from_dict = StreamMerkleFinalizeRequest.from_dict(stream_merkle_finalize_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


