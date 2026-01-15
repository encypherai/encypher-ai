# VerifyAdvancedRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** |  | 
**include_attribution** | **bool** |  | [optional] [default to False]
**detect_plagiarism** | **bool** |  | [optional] [default to False]
**include_heat_map** | **bool** |  | [optional] [default to False]
**min_match_percentage** | **float** |  | [optional] [default to 0.0]
**segmentation_level** | **str** |  | [optional] [default to 'sentence']
**search_scope** | **str** |  | [optional] [default to 'organization']

## Example

```python
from encypher.models.verify_advanced_request import VerifyAdvancedRequest

# TODO update the JSON string below
json = "{}"
# create an instance of VerifyAdvancedRequest from a JSON string
verify_advanced_request_instance = VerifyAdvancedRequest.from_json(json)
# print the JSON string representation of the object
print(VerifyAdvancedRequest.to_json())

# convert the object into a dict
verify_advanced_request_dict = verify_advanced_request_instance.to_dict()
# create an instance of VerifyAdvancedRequest from a dict
verify_advanced_request_from_dict = VerifyAdvancedRequest.from_dict(verify_advanced_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


