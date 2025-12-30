# DocumentDetail

Detailed document information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** |  | 
**title** | **str** |  | [optional] 
**document_type** | **str** |  | [optional] 
**status** | **str** |  | [optional] [default to 'active']
**signed_at** | **str** |  | 
**verification_url** | **str** |  | 
**word_count** | **int** |  | [optional] 
**url** | **str** |  | [optional] 
**signer_id** | **str** |  | [optional] 
**revoked_at** | **str** |  | [optional] 
**revoked_reason** | **str** |  | [optional] 

## Example

```python
from encypher.models.document_detail import DocumentDetail

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentDetail from a JSON string
document_detail_instance = DocumentDetail.from_json(json)
# print the JSON string representation of the object
print(DocumentDetail.to_json())

# convert the object into a dict
document_detail_dict = document_detail_instance.to_dict()
# create an instance of DocumentDetail from a dict
document_detail_from_dict = DocumentDetail.from_dict(document_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


