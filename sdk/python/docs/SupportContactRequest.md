# SupportContactRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subject** | **str** |  |
**message** | **str** |  |
**category** | **str** |  | [optional] [default to 'general']

## Example

```python
from encypher.models.support_contact_request import SupportContactRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SupportContactRequest from a JSON string
support_contact_request_instance = SupportContactRequest.from_json(json)
# print the JSON string representation of the object
print(SupportContactRequest.to_json())

# convert the object into a dict
support_contact_request_dict = support_contact_request_instance.to_dict()
# create an instance of SupportContactRequest from a dict
support_contact_request_from_dict = SupportContactRequest.from_dict(support_contact_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
