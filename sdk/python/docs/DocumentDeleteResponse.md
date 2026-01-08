# DocumentDeleteResponse

Response for document deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 

## Example

```python
from encypher.models.document_delete_response import DocumentDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentDeleteResponse from a JSON string
document_delete_response_instance = DocumentDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentDeleteResponse.to_json())

# convert the object into a dict
document_delete_response_dict = document_delete_response_instance.to_dict()
# create an instance of DocumentDeleteResponse from a dict
document_delete_response_from_dict = DocumentDeleteResponse.from_dict(document_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


