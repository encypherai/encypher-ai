# C2PASchemaCreate

Request schema for creating a C2PA assertion schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Human-readable name for the schema | 
**label** | **str** | Full assertion label (e.g., &#39;com.acme.legal.v1&#39;) | 
**version** | **str** | Schema version (e.g., &#39;v1&#39;, &#39;1.0.0&#39;) | [optional] [default to '1.0']
**json_schema** | **Dict[str, object]** | JSON Schema for validation | 
**description** | **str** |  | [optional] 
**is_public** | **bool** | Whether schema is publicly accessible | [optional] [default to False]

## Example

```python
from encypher.models.c2_pa_schema_create import C2PASchemaCreate

# TODO update the JSON string below
json = "{}"
# create an instance of C2PASchemaCreate from a JSON string
c2_pa_schema_create_instance = C2PASchemaCreate.from_json(json)
# print the JSON string representation of the object
print(C2PASchemaCreate.to_json())

# convert the object into a dict
c2_pa_schema_create_dict = c2_pa_schema_create_instance.to_dict()
# create an instance of C2PASchemaCreate from a dict
c2_pa_schema_create_from_dict = C2PASchemaCreate.from_dict(c2_pa_schema_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


