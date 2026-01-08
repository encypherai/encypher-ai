# DocumentHistoryResponse

Response for document history.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 

## Example

```python
from encypher.models.document_history_response import DocumentHistoryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentHistoryResponse from a JSON string
document_history_response_instance = DocumentHistoryResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentHistoryResponse.to_json())

# convert the object into a dict
document_history_response_dict = document_history_response_instance.to_dict()
# create an instance of DocumentHistoryResponse from a dict
document_history_response_from_dict = DocumentHistoryResponse.from_dict(document_history_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


