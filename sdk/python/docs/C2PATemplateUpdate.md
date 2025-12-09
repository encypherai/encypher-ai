# C2PATemplateUpdate

Request schema for updating an assertion template.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**template_data** | **Dict[str, object]** |  | [optional] 
**category** | **str** |  | [optional] 
**is_public** | **bool** |  | [optional] 

## Example

```python
from encypher.models.c2_pa_template_update import C2PATemplateUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of C2PATemplateUpdate from a JSON string
c2_pa_template_update_instance = C2PATemplateUpdate.from_json(json)
# print the JSON string representation of the object
print(C2PATemplateUpdate.to_json())

# convert the object into a dict
c2_pa_template_update_dict = c2_pa_template_update_instance.to_dict()
# create an instance of C2PATemplateUpdate from a dict
c2_pa_template_update_from_dict = C2PATemplateUpdate.from_dict(c2_pa_template_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


