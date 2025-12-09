# C2PASchemaResponse

Response schema for C2PA assertion schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**label** | **str** |  | 
**version** | **str** |  | 
**json_schema** | **Dict[str, object]** |  | 
**description** | **str** |  | 
**organization_id** | **str** |  | 
**is_active** | **bool** |  | 
**is_public** | **bool** |  | 
**created_at** | **str** |  | 
**updated_at** | **str** |  | 

## Example

```python
from encypher.models.c2_pa_schema_response import C2PASchemaResponse

# TODO update the JSON string below
json = "{}"
# create an instance of C2PASchemaResponse from a JSON string
c2_pa_schema_response_instance = C2PASchemaResponse.from_json(json)
# print the JSON string representation of the object
print(C2PASchemaResponse.to_json())

# convert the object into a dict
c2_pa_schema_response_dict = c2_pa_schema_response_instance.to_dict()
# create an instance of C2PASchemaResponse from a dict
c2_pa_schema_response_from_dict = C2PASchemaResponse.from_dict(c2_pa_schema_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


