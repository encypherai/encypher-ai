# LicensingAgreementCreate

Schema for creating a licensing agreement.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agreement_name** | **str** |  | 
**ai_company_name** | **str** |  | 
**ai_company_email** | **str** |  | 
**agreement_type** | [**AgreementType**](AgreementType.md) |  | [optional] 
**total_value** | [**TotalValue**](TotalValue.md) |  | 
**currency** | **str** |  | [optional] [default to 'USD']
**start_date** | **date** |  | 
**end_date** | **date** |  | 
**content_types** | **List[str]** |  | [optional] 
**min_word_count** | **int** |  | [optional] 

## Example

```python
from encypher.models.licensing_agreement_create import LicensingAgreementCreate

# TODO update the JSON string below
json = "{}"
# create an instance of LicensingAgreementCreate from a JSON string
licensing_agreement_create_instance = LicensingAgreementCreate.from_json(json)
# print the JSON string representation of the object
print(LicensingAgreementCreate.to_json())

# convert the object into a dict
licensing_agreement_create_dict = licensing_agreement_create_instance.to_dict()
# create an instance of LicensingAgreementCreate from a dict
licensing_agreement_create_from_dict = LicensingAgreementCreate.from_dict(licensing_agreement_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


