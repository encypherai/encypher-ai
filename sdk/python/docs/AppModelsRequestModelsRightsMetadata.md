# AppModelsRequestModelsRightsMetadata


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**copyright_holder** | **str** |  | [optional] 
**license_url** | **str** |  | [optional] 
**usage_terms** | **str** |  | [optional] 
**syndication_allowed** | **bool** |  | [optional] 
**embargo_until** | **datetime** |  | [optional] 
**contact_email** | **str** |  | [optional] 

## Example

```python
from encypher.models.app_models_request_models_rights_metadata import AppModelsRequestModelsRightsMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of AppModelsRequestModelsRightsMetadata from a JSON string
app_models_request_models_rights_metadata_instance = AppModelsRequestModelsRightsMetadata.from_json(json)
# print the JSON string representation of the object
print(AppModelsRequestModelsRightsMetadata.to_json())

# convert the object into a dict
app_models_request_models_rights_metadata_dict = app_models_request_models_rights_metadata_instance.to_dict()
# create an instance of AppModelsRequestModelsRightsMetadata from a dict
app_models_request_models_rights_metadata_from_dict = AppModelsRequestModelsRightsMetadata.from_dict(app_models_request_models_rights_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


