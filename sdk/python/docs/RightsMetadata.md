# RightsMetadata


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**copyright_holder** | **str** |  | [optional] 
**license_url** | **str** |  | [optional] 
**usage_terms** | **str** |  | [optional] 
**syndication_allowed** | **bool** |  | [optional] 
**embargo_until** | **datetime** |  | [optional] 
**contact_email** | **str** |  | [optional] 

## Example

```python
from encypher.models.rights_metadata import RightsMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of RightsMetadata from a JSON string
rights_metadata_instance = RightsMetadata.from_json(json)
# print the JSON string representation of the object
print(RightsMetadata.to_json())

# convert the object into a dict
rights_metadata_dict = rights_metadata_instance.to_dict()
# create an instance of RightsMetadata from a dict
rights_metadata_from_dict = RightsMetadata.from_dict(rights_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


