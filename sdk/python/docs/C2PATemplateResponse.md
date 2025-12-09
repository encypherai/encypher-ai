# C2PATemplateResponse

Response schema for assertion template.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**description** | **str** |  | 
**schema_id** | **str** |  | 
**template_data** | **Dict[str, object]** |  | 
**category** | **str** |  | 
**organization_id** | **str** |  | 
**is_default** | **bool** |  | 
**is_active** | **bool** |  | 
**is_public** | **bool** |  | 
**created_at** | **str** |  | 
**updated_at** | **str** |  | 

## Example

```python
from encypher.models.c2_pa_template_response import C2PATemplateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of C2PATemplateResponse from a JSON string
c2_pa_template_response_instance = C2PATemplateResponse.from_json(json)
# print the JSON string representation of the object
print(C2PATemplateResponse.to_json())

# convert the object into a dict
c2_pa_template_response_dict = c2_pa_template_response_instance.to_dict()
# create an instance of C2PATemplateResponse from a dict
c2_pa_template_response_from_dict = C2PATemplateResponse.from_dict(c2_pa_template_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


