# SignRequest

Request model for signing content.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Content to sign | 
**document_id** | **str** |  | [optional] 
**document_title** | **str** |  | [optional] 
**document_url** | **str** |  | [optional] 
**document_type** | **str** | Document type: article | legal_brief | contract | ai_output | [optional] [default to 'article']
**claim_generator** | **str** |  | [optional] 
**actions** | **List[Dict[str, object]]** |  | [optional] 
**template_id** | **str** |  | [optional] 
**validate_assertions** | **bool** | Whether to validate template-based assertions (Business+). | [optional] [default to True]
**rights** | [**RightsMetadata**](RightsMetadata.md) |  | [optional] 

## Example

```python
from encypher.models.sign_request import SignRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SignRequest from a JSON string
sign_request_instance = SignRequest.from_json(json)
# print the JSON string representation of the object
print(SignRequest.to_json())

# convert the object into a dict
sign_request_dict = sign_request_instance.to_dict()
# create an instance of SignRequest from a dict
sign_request_from_dict = SignRequest.from_dict(sign_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


