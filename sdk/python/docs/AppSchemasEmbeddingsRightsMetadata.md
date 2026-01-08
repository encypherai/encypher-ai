# AppSchemasEmbeddingsRightsMetadata


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
from encypher.models.app_schemas_embeddings_rights_metadata import AppSchemasEmbeddingsRightsMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of AppSchemasEmbeddingsRightsMetadata from a JSON string
app_schemas_embeddings_rights_metadata_instance = AppSchemasEmbeddingsRightsMetadata.from_json(json)
# print the JSON string representation of the object
print(AppSchemasEmbeddingsRightsMetadata.to_json())

# convert the object into a dict
app_schemas_embeddings_rights_metadata_dict = app_schemas_embeddings_rights_metadata_instance.to_dict()
# create an instance of AppSchemasEmbeddingsRightsMetadata from a dict
app_schemas_embeddings_rights_metadata_from_dict = AppSchemasEmbeddingsRightsMetadata.from_dict(app_schemas_embeddings_rights_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


