# LicensingAgreementResponse

Schema for licensing agreement response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**agreement_name** | **str** |  | 
**ai_company_id** | **str** |  | 
**agreement_type** | [**AgreementType**](AgreementType.md) |  | 
**total_value** | **str** |  | 
**currency** | **str** |  | 
**start_date** | **date** |  | 
**end_date** | **date** |  | 
**content_types** | **List[str]** |  | 
**min_word_count** | **int** |  | 
**status** | [**AgreementStatus**](AgreementStatus.md) |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from encypher.models.licensing_agreement_response import LicensingAgreementResponse

# TODO update the JSON string below
json = "{}"
# create an instance of LicensingAgreementResponse from a JSON string
licensing_agreement_response_instance = LicensingAgreementResponse.from_json(json)
# print the JSON string representation of the object
print(LicensingAgreementResponse.to_json())

# convert the object into a dict
licensing_agreement_response_dict = licensing_agreement_response_instance.to_dict()
# create an instance of LicensingAgreementResponse from a dict
licensing_agreement_response_from_dict = LicensingAgreementResponse.from_dict(licensing_agreement_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


