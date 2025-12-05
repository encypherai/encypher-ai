# BatchVerifyResult

Result for a single embedding in batch verification.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ref_id** | **str** | Reference ID | 
**valid** | **bool** | Whether embedding is valid | 
**document_id** | **str** |  | [optional] 
**text_preview** | **str** |  | [optional] 
**error** | **str** |  | [optional] 

## Example

```python
from encypher.models.batch_verify_result import BatchVerifyResult

# TODO update the JSON string below
json = "{}"
# create an instance of BatchVerifyResult from a JSON string
batch_verify_result_instance = BatchVerifyResult.from_json(json)
# print the JSON string representation of the object
print(BatchVerifyResult.to_json())

# convert the object into a dict
batch_verify_result_dict = batch_verify_result_instance.to_dict()
# create an instance of BatchVerifyResult from a dict
batch_verify_result_from_dict = BatchVerifyResult.from_dict(batch_verify_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


