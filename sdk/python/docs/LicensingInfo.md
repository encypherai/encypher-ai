# LicensingInfo

Licensing information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**license_type** | **str** | License type | 
**license_url** | **str** |  | [optional] 
**usage_terms** | **str** |  | [optional] 
**contact_email** | **str** |  | [optional] 

## Example

```python
from encypher.models.licensing_info import LicensingInfo

# TODO update the JSON string below
json = "{}"
# create an instance of LicensingInfo from a JSON string
licensing_info_instance = LicensingInfo.from_json(json)
# print the JSON string representation of the object
print(LicensingInfo.to_json())

# convert the object into a dict
licensing_info_dict = licensing_info_instance.to_dict()
# create an instance of LicensingInfo from a dict
licensing_info_from_dict = LicensingInfo.from_dict(licensing_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


