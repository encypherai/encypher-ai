# AppSchemasEmbeddingsErrorResponse

Error response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Always false for errors | [optional] [default to False]
**error** | **str** | Error message | 
**detail** | **str** |  | [optional] 
**error_code** | **str** |  | [optional] 

## Example

```python
from encypher.models.app_schemas_embeddings_error_response import AppSchemasEmbeddingsErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AppSchemasEmbeddingsErrorResponse from a JSON string
app_schemas_embeddings_error_response_instance = AppSchemasEmbeddingsErrorResponse.from_json(json)
# print the JSON string representation of the object
print(AppSchemasEmbeddingsErrorResponse.to_json())

# convert the object into a dict
app_schemas_embeddings_error_response_dict = app_schemas_embeddings_error_response_instance.to_dict()
# create an instance of AppSchemasEmbeddingsErrorResponse from a dict
app_schemas_embeddings_error_response_from_dict = AppSchemasEmbeddingsErrorResponse.from_dict(app_schemas_embeddings_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


