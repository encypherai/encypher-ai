# DocumentVerify

Schema for complete document verification

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** |  | 
**content** | **str** |  | 

## Example

```python
from encypher.models.document_verify import DocumentVerify

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentVerify from a JSON string
document_verify_instance = DocumentVerify.from_json(json)
# print the JSON string representation of the object
print(DocumentVerify.to_json())

# convert the object into a dict
document_verify_dict = document_verify_instance.to_dict()
# create an instance of DocumentVerify from a dict
document_verify_from_dict = DocumentVerify.from_dict(document_verify_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


