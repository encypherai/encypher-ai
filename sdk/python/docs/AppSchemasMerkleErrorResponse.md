# AppSchemasMerkleErrorResponse

Standard error response schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Always false for errors | [optional] [default to False]
**error** | **str** | Error type | 
**message** | **str** | Human-readable error message | 
**details** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.app_schemas_merkle_error_response import AppSchemasMerkleErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AppSchemasMerkleErrorResponse from a JSON string
app_schemas_merkle_error_response_instance = AppSchemasMerkleErrorResponse.from_json(json)
# print the JSON string representation of the object
print(AppSchemasMerkleErrorResponse.to_json())

# convert the object into a dict
app_schemas_merkle_error_response_dict = app_schemas_merkle_error_response_instance.to_dict()
# create an instance of AppSchemasMerkleErrorResponse from a dict
app_schemas_merkle_error_response_from_dict = AppSchemasMerkleErrorResponse.from_dict(app_schemas_merkle_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


