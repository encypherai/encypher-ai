# BatchItemResult

Per-item response object emitted in batch responses.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Document identifier from request | 
**status** | **str** | Processing outcome for the document | 
**signed_text** | **str** |  | [optional] 
**embedded_content** | **str** |  | [optional] 
**verdict** | [**VerifyVerdict**](VerifyVerdict.md) |  | [optional] 
**error_code** | **str** |  | [optional] 
**error_message** | **str** |  | [optional] 
**statistics** | **Dict[str, object]** | Timing and segmentation statistics for the item | [optional] 

## Example

```python
from encypher.models.batch_item_result import BatchItemResult

# TODO update the JSON string below
json = "{}"
# create an instance of BatchItemResult from a JSON string
batch_item_result_instance = BatchItemResult.from_json(json)
# print the JSON string representation of the object
print(BatchItemResult.to_json())

# convert the object into a dict
batch_item_result_dict = batch_item_result_instance.to_dict()
# create an instance of BatchItemResult from a dict
batch_item_result_from_dict = BatchItemResult.from_dict(batch_item_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


