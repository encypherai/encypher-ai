# DocumentInfo

Document information from verification.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Document identifier | 
**title** | **str** |  | [optional] 
**published_at** | **datetime** |  | [optional] 
**author** | **str** |  | [optional] 
**organization** | **str** | Organization name | 

## Example

```python
from encypher.models.document_info import DocumentInfo

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentInfo from a JSON string
document_info_instance = DocumentInfo.from_json(json)
# print the JSON string representation of the object
print(DocumentInfo.to_json())

# convert the object into a dict
document_info_dict = document_info_instance.to_dict()
# create an instance of DocumentInfo from a dict
document_info_from_dict = DocumentInfo.from_dict(document_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


