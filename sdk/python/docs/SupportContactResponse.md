# SupportContactResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | [**SupportResponseData**](SupportResponseData.md) |  |

## Example

```python
from encypher.models.support_contact_response import SupportContactResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SupportContactResponse from a JSON string
support_contact_response_instance = SupportContactResponse.from_json(json)
# print the JSON string representation of the object
print(SupportContactResponse.to_json())

# convert the object into a dict
support_contact_response_dict = support_contact_response_instance.to_dict()
# create an instance of SupportContactResponse from a dict
support_contact_response_from_dict = SupportContactResponse.from_dict(support_contact_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
