# VerificationServiceLicensingInfo

Content licensing information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**license_type** | **str** |  | [optional] 
**license_url** | **str** |  | [optional] 
**usage_terms** | **str** |  | [optional] 
**attribution_required** | **bool** |  | [optional] [default to False]

## Example

```python
from encypher.models.verification_service_licensing_info import VerificationServiceLicensingInfo

# TODO update the JSON string below
json = "{}"
# create an instance of VerificationServiceLicensingInfo from a JSON string
verification_service_licensing_info_instance = VerificationServiceLicensingInfo.from_json(json)
# print the JSON string representation of the object
print(VerificationServiceLicensingInfo.to_json())

# convert the object into a dict
verification_service_licensing_info_dict = verification_service_licensing_info_instance.to_dict()
# create an instance of VerificationServiceLicensingInfo from a dict
verification_service_licensing_info_from_dict = VerificationServiceLicensingInfo.from_dict(verification_service_licensing_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


