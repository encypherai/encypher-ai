# BatchVerifyResponse

Response from batch verification.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | [**List[BatchVerifyResult]**](BatchVerifyResult.md) | Verification results | 
**total** | **int** | Total number of embeddings checked | 
**valid_count** | **int** | Number of valid embeddings | 
**invalid_count** | **int** | Number of invalid embeddings | 

## Example

```python
from encypher.models.batch_verify_response import BatchVerifyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BatchVerifyResponse from a JSON string
batch_verify_response_instance = BatchVerifyResponse.from_json(json)
# print the JSON string representation of the object
print(BatchVerifyResponse.to_json())

# convert the object into a dict
batch_verify_response_dict = batch_verify_response_instance.to_dict()
# create an instance of BatchVerifyResponse from a dict
batch_verify_response_from_dict = BatchVerifyResponse.from_dict(batch_verify_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


