# VerificationServiceErrorDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** |  | 
**message** | **str** |  | 
**hint** | **str** |  | [optional] 

## Example

```python
from encypher.models.verification_service_error_detail import VerificationServiceErrorDetail

# TODO update the JSON string below
json = "{}"
# create an instance of VerificationServiceErrorDetail from a JSON string
verification_service_error_detail_instance = VerificationServiceErrorDetail.from_json(json)
# print the JSON string representation of the object
print(VerificationServiceErrorDetail.to_json())

# convert the object into a dict
verification_service_error_detail_dict = verification_service_error_detail_instance.to_dict()
# create an instance of VerificationServiceErrorDetail from a dict
verification_service_error_detail_from_dict = VerificationServiceErrorDetail.from_dict(verification_service_error_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


