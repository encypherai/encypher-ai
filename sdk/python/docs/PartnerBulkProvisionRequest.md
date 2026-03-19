# PartnerBulkProvisionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**publishers** | [**List[PartnerPublisherSpec]**](PartnerPublisherSpec.md) |  |
**partner_name** | **str** |  |
**default_template** | **str** |  | [optional] [default to 'news_publisher_default']
**coalition_member** | **bool** |  | [optional] [default to True]
**send_claim_email** | **bool** |  | [optional] [default to True]

## Example

```python
from encypher.models.partner_bulk_provision_request import PartnerBulkProvisionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PartnerBulkProvisionRequest from a JSON string
partner_bulk_provision_request_instance = PartnerBulkProvisionRequest.from_json(json)
# print the JSON string representation of the object
print(PartnerBulkProvisionRequest.to_json())

# convert the object into a dict
partner_bulk_provision_request_dict = partner_bulk_provision_request_instance.to_dict()
# create an instance of PartnerBulkProvisionRequest from a dict
partner_bulk_provision_request_from_dict = PartnerBulkProvisionRequest.from_dict(partner_bulk_provision_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
