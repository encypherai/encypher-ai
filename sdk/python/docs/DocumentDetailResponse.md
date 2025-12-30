# DocumentDetailResponse

Response for single document.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | [**DocumentDetail**](DocumentDetail.md) |  | 

## Example

```python
from encypher.models.document_detail_response import DocumentDetailResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentDetailResponse from a JSON string
document_detail_response_instance = DocumentDetailResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentDetailResponse.to_json())

# convert the object into a dict
document_detail_response_dict = document_detail_response_instance.to_dict()
# create an instance of DocumentDetailResponse from a dict
document_detail_response_from_dict = DocumentDetailResponse.from_dict(document_detail_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


