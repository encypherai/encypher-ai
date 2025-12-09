# DocumentStatusResponse

Response for document status query.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** |  | 
**organization_id** | **str** |  | 
**revoked** | **bool** |  | 
**revoked_at** | **str** |  | [optional] 
**revoked_reason** | **str** |  | [optional] 
**revoked_reason_detail** | **str** |  | [optional] 
**reinstated_at** | **str** |  | [optional] 
**status_list_url** | **str** |  | [optional] 
**status_list_index** | **int** |  | [optional] 
**status_bit_index** | **int** |  | [optional] 

## Example

```python
from encypher.models.document_status_response import DocumentStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentStatusResponse from a JSON string
document_status_response_instance = DocumentStatusResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentStatusResponse.to_json())

# convert the object into a dict
document_status_response_dict = document_status_response_instance.to_dict()
# create an instance of DocumentStatusResponse from a dict
document_status_response_from_dict = DocumentStatusResponse.from_dict(document_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


