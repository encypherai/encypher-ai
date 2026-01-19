# BatchVerifyRequest

Request to verify multiple embeddings.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**references** | [**List[VerifyEmbeddingRequest]**](VerifyEmbeddingRequest.md) | List of embeddings to verify | 

## Example

```python
from encypher.models.batch_verify_request import BatchVerifyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BatchVerifyRequest from a JSON string
batch_verify_request_instance = BatchVerifyRequest.from_json(json)
# print the JSON string representation of the object
print(BatchVerifyRequest.to_json())

# convert the object into a dict
batch_verify_request_dict = batch_verify_request_instance.to_dict()
# create an instance of BatchVerifyRequest from a dict
batch_verify_request_from_dict = BatchVerifyRequest.from_dict(batch_verify_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


