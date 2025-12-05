# C2PATemplateListResponse

Response schema for listing templates.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**templates** | [**List[C2PATemplateResponse]**](C2PATemplateResponse.md) |  | 
**total** | **int** |  | 
**page** | **int** |  | 
**page_size** | **int** |  | 

## Example

```python
from encypher.models.c2_pa_template_list_response import C2PATemplateListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of C2PATemplateListResponse from a JSON string
c2_pa_template_list_response_instance = C2PATemplateListResponse.from_json(json)
# print the JSON string representation of the object
print(C2PATemplateListResponse.to_json())

# convert the object into a dict
c2_pa_template_list_response_dict = c2_pa_template_list_response_instance.to_dict()
# create an instance of C2PATemplateListResponse from a dict
c2_pa_template_list_response_from_dict = C2PATemplateListResponse.from_dict(c2_pa_template_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


