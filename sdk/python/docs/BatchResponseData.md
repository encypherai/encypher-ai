# BatchResponseData

Top-level data payload for batch responses.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | [**List[BatchItemResult]**](BatchItemResult.md) | Per-item results | 
**summary** | [**BatchSummary**](BatchSummary.md) | Aggregate stats for the batch | 

## Example

```python
from encypher.models.batch_response_data import BatchResponseData

# TODO update the JSON string below
json = "{}"
# create an instance of BatchResponseData from a JSON string
batch_response_data_instance = BatchResponseData.from_json(json)
# print the JSON string representation of the object
print(BatchResponseData.to_json())

# convert the object into a dict
batch_response_data_dict = batch_response_data_instance.to_dict()
# create an instance of BatchResponseData from a dict
batch_response_data_from_dict = BatchResponseData.from_dict(batch_response_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


