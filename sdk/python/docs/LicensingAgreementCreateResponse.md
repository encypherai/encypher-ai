# LicensingAgreementCreateResponse

Schema for licensing agreement creation response (includes API key).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**agreement_name** | **str** |  | 
**api_key** | **str** |  | 
**api_key_prefix** | **str** |  | 
**status** | [**AgreementStatus**](AgreementStatus.md) |  | 
**created_at** | **datetime** |  | 

## Example

```python
from encypher.models.licensing_agreement_create_response import LicensingAgreementCreateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of LicensingAgreementCreateResponse from a JSON string
licensing_agreement_create_response_instance = LicensingAgreementCreateResponse.from_json(json)
# print the JSON string representation of the object
print(LicensingAgreementCreateResponse.to_json())

# convert the object into a dict
licensing_agreement_create_response_dict = licensing_agreement_create_response_instance.to_dict()
# create an instance of LicensingAgreementCreateResponse from a dict
licensing_agreement_create_response_from_dict = LicensingAgreementCreateResponse.from_dict(licensing_agreement_create_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


