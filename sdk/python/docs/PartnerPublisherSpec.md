# PartnerPublisherSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  |
**contact_email** | **str** |  |
**domain** | **str** |  | [optional]
**template** | **str** |  | [optional] [default to 'news_publisher_default']
**notice_status** | **str** |  | [optional] [default to 'active']

## Example

```python
from encypher.models.partner_publisher_spec import PartnerPublisherSpec

# TODO update the JSON string below
json = "{}"
# create an instance of PartnerPublisherSpec from a JSON string
partner_publisher_spec_instance = PartnerPublisherSpec.from_json(json)
# print the JSON string representation of the object
print(PartnerPublisherSpec.to_json())

# convert the object into a dict
partner_publisher_spec_dict = partner_publisher_spec_instance.to_dict()
# create an instance of PartnerPublisherSpec from a dict
partner_publisher_spec_from_dict = PartnerPublisherSpec.from_dict(partner_publisher_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
