# LicensingAgreementUpdate

Schema for updating a licensing agreement.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agreement_name** | **str** |  | [optional] 
**total_value** | [**TotalValue1**](TotalValue1.md) |  | [optional] 
**end_date** | **date** |  | [optional] 
**content_types** | **List[str]** |  | [optional] 
**min_word_count** | **int** |  | [optional] 
**status** | [**AgreementStatus**](AgreementStatus.md) |  | [optional] 

## Example

```python
from encypher.models.licensing_agreement_update import LicensingAgreementUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of LicensingAgreementUpdate from a JSON string
licensing_agreement_update_instance = LicensingAgreementUpdate.from_json(json)
# print the JSON string representation of the object
print(LicensingAgreementUpdate.to_json())

# convert the object into a dict
licensing_agreement_update_dict = licensing_agreement_update_instance.to_dict()
# create an instance of LicensingAgreementUpdate from a dict
licensing_agreement_update_from_dict = LicensingAgreementUpdate.from_dict(licensing_agreement_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


