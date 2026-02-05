# VerificationServiceC2PAInfo

C2PA manifest information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**manifest_url** | **str** |  | [optional] 
**manifest_hash** | **str** |  | [optional] 
**validated** | **bool** |  | [optional] [default to False]
**validation_type** | **str** |  | [optional] 
**assertions** | **List[Dict[str, object]]** |  | [optional] 
**certificate_chain** | **List[str]** |  | [optional] 

## Example

```python
from encypher.models.verification_service_c2_pa_info import VerificationServiceC2PAInfo

# TODO update the JSON string below
json = "{}"
# create an instance of VerificationServiceC2PAInfo from a JSON string
verification_service_c2_pa_info_instance = VerificationServiceC2PAInfo.from_json(json)
# print the JSON string representation of the object
print(VerificationServiceC2PAInfo.to_json())

# convert the object into a dict
verification_service_c2_pa_info_dict = verification_service_c2_pa_info_instance.to_dict()
# create an instance of VerificationServiceC2PAInfo from a dict
verification_service_c2_pa_info_from_dict = VerificationServiceC2PAInfo.from_dict(verification_service_c2_pa_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


