# AppSchemasEmbeddingsBatchVerifyRequest

Request to verify multiple embeddings.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**references** | [**List[VerifyEmbeddingRequest]**](VerifyEmbeddingRequest.md) | List of embeddings to verify |

## Example

```python
from encypher.models.app_schemas_embeddings_batch_verify_request import AppSchemasEmbeddingsBatchVerifyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AppSchemasEmbeddingsBatchVerifyRequest from a JSON string
app_schemas_embeddings_batch_verify_request_instance = AppSchemasEmbeddingsBatchVerifyRequest.from_json(json)
# print the JSON string representation of the object
print(AppSchemasEmbeddingsBatchVerifyRequest.to_json())

# convert the object into a dict
app_schemas_embeddings_batch_verify_request_dict = app_schemas_embeddings_batch_verify_request_instance.to_dict()
# create an instance of AppSchemasEmbeddingsBatchVerifyRequest from a dict
app_schemas_embeddings_batch_verify_request_from_dict = AppSchemasEmbeddingsBatchVerifyRequest.from_dict(app_schemas_embeddings_batch_verify_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
