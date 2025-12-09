# BatchItemPayload

Single document payload within a batch request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Unique document identifier | 
**text** | **str** | Raw document text to process | 
**title** | **str** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.batch_item_payload import BatchItemPayload

# TODO update the JSON string below
json = "{}"
# create an instance of BatchItemPayload from a JSON string
batch_item_payload_instance = BatchItemPayload.from_json(json)
# print the JSON string representation of the object
print(BatchItemPayload.to_json())

# convert the object into a dict
batch_item_payload_dict = batch_item_payload_instance.to_dict()
# create an instance of BatchItemPayload from a dict
batch_item_payload_from_dict = BatchItemPayload.from_dict(batch_item_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


