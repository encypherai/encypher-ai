# C2PAInfo

C2PA manifest information with verification details.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**manifest_url** | **str** | C2PA manifest URL | 
**manifest_hash** | **str** |  | [optional] 
**validated** | **bool** | Whether the manifest passed validation | 
**validation_type** | **str** | Validation semantics. | 
**validation_details** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.c2_pa_info import C2PAInfo

# TODO update the JSON string below
json = "{}"
# create an instance of C2PAInfo from a JSON string
c2_pa_info_instance = C2PAInfo.from_json(json)
# print the JSON string representation of the object
print(C2PAInfo.to_json())

# convert the object into a dict
c2_pa_info_dict = c2_pa_info_instance.to_dict()
# create an instance of C2PAInfo from a dict
c2_pa_info_from_dict = C2PAInfo.from_dict(c2_pa_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


