# VerificationServiceDocumentInfo

Document metadata from the embedding.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**author** | **str** |  | [optional] 
**published_at** | **datetime** |  | [optional] 
**document_type** | **str** |  | [optional] 

## Example

```python
from encypher.models.verification_service_document_info import VerificationServiceDocumentInfo

# TODO update the JSON string below
json = "{}"
# create an instance of VerificationServiceDocumentInfo from a JSON string
verification_service_document_info_instance = VerificationServiceDocumentInfo.from_json(json)
# print the JSON string representation of the object
print(VerificationServiceDocumentInfo.to_json())

# convert the object into a dict
verification_service_document_info_dict = verification_service_document_info_instance.to_dict()
# create an instance of VerificationServiceDocumentInfo from a dict
verification_service_document_info_from_dict = VerificationServiceDocumentInfo.from_dict(verification_service_document_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


