# SignDocument

A single document in a batch sign request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Content to sign | 
**document_id** | **str** |  | [optional] 
**document_title** | **str** |  | [optional] 
**document_url** | **str** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.sign_document import SignDocument

# TODO update the JSON string below
json = "{}"
# create an instance of SignDocument from a JSON string
sign_document_instance = SignDocument.from_json(json)
# print the JSON string representation of the object
print(SignDocument.to_json())

# convert the object into a dict
sign_document_dict = sign_document_instance.to_dict()
# create an instance of SignDocument from a dict
sign_document_from_dict = SignDocument.from_dict(sign_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


