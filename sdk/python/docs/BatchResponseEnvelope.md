# BatchResponseEnvelope

Envelope returned by batch endpoints.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Indicates whether the batch request succeeded | 
**batch_id** | **str** | Batch request identifier | 
**data** | [**BatchResponseData**](BatchResponseData.md) |  | [optional] 
**error** | [**ErrorDetail**](ErrorDetail.md) |  | [optional] 
**correlation_id** | **str** | Request correlation identifier for tracing | 

## Example

```python
from encypher.models.batch_response_envelope import BatchResponseEnvelope

# TODO update the JSON string below
json = "{}"
# create an instance of BatchResponseEnvelope from a JSON string
batch_response_envelope_instance = BatchResponseEnvelope.from_json(json)
# print the JSON string representation of the object
print(BatchResponseEnvelope.to_json())

# convert the object into a dict
batch_response_envelope_dict = batch_response_envelope_instance.to_dict()
# create an instance of BatchResponseEnvelope from a dict
batch_response_envelope_from_dict = BatchResponseEnvelope.from_dict(batch_response_envelope_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


