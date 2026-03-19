# RichSignOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**segmentation_level** | **str** |  | [optional] [default to 'sentence']
**manifest_mode** | **str** |  | [optional] [default to 'micro']
**action** | **str** |  | [optional] [default to 'c2pa.created']
**enable_trustmark** | **bool** |  | [optional] [default to False]
**image_quality** | **int** |  | [optional] [default to 95]
**use_rights_profile** | **bool** |  | [optional] [default to True]
**index_for_attribution** | **bool** |  | [optional] [default to True]

## Example

```python
from encypher.models.rich_sign_options import RichSignOptions

# TODO update the JSON string below
json = "{}"
# create an instance of RichSignOptions from a JSON string
rich_sign_options_instance = RichSignOptions.from_json(json)
# print the JSON string representation of the object
print(RichSignOptions.to_json())

# convert the object into a dict
rich_sign_options_dict = rich_sign_options_instance.to_dict()
# create an instance of RichSignOptions from a dict
rich_sign_options_from_dict = RichSignOptions.from_dict(rich_sign_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
