# C2PASchemaUpdate

Request schema for updating a C2PA assertion schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**json_schema** | **Dict[str, object]** |  | [optional] 
**description** | **str** |  | [optional] 
**is_public** | **bool** |  | [optional] 

## Example

```python
from encypher.models.c2_pa_schema_update import C2PASchemaUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of C2PASchemaUpdate from a JSON string
c2_pa_schema_update_instance = C2PASchemaUpdate.from_json(json)
# print the JSON string representation of the object
print(C2PASchemaUpdate.to_json())

# convert the object into a dict
c2_pa_schema_update_dict = c2_pa_schema_update_instance.to_dict()
# create an instance of C2PASchemaUpdate from a dict
c2_pa_schema_update_from_dict = C2PASchemaUpdate.from_dict(c2_pa_schema_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


