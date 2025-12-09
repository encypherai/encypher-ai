# C2PATemplateCreate

Request schema for creating an assertion template.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Template name | 
**schema_id** | **str** | ID of the schema this template uses | 
**template_data** | **Dict[str, object]** | Template data/configuration | 
**description** | **str** |  | [optional] 
**category** | **str** |  | [optional] 
**is_public** | **bool** | Whether template is publicly accessible | [optional] [default to False]

## Example

```python
from encypher.models.c2_pa_template_create import C2PATemplateCreate

# TODO update the JSON string below
json = "{}"
# create an instance of C2PATemplateCreate from a JSON string
c2_pa_template_create_instance = C2PATemplateCreate.from_json(json)
# print the JSON string representation of the object
print(C2PATemplateCreate.to_json())

# convert the object into a dict
c2_pa_template_create_dict = c2_pa_template_create_instance.to_dict()
# create an instance of C2PATemplateCreate from a dict
c2_pa_template_create_from_dict = C2PATemplateCreate.from_dict(c2_pa_template_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


