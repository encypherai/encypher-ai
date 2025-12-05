# VerifyEmbeddingRequest

Request to verify an embedding (for batch operations).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ref_id** | **str** | Reference ID (8 hex characters) | 
**signature** | **str** | Signature (8+ hex characters) | 

## Example

```python
from encypher.models.verify_embedding_request import VerifyEmbeddingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of VerifyEmbeddingRequest from a JSON string
verify_embedding_request_instance = VerifyEmbeddingRequest.from_json(json)
# print the JSON string representation of the object
print(VerifyEmbeddingRequest.to_json())

# convert the object into a dict
verify_embedding_request_dict = verify_embedding_request_instance.to_dict()
# create an instance of VerifyEmbeddingRequest from a dict
verify_embedding_request_from_dict = VerifyEmbeddingRequest.from_dict(verify_embedding_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


